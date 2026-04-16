"""
Coffee Export MT Conversion App v3
====================================
Reads a single 'data' sheet from raw export files.
Splits into Coffee / Chicory by HS CODE, applies exclusion list, converts to MT.

Setup:
    pip install streamlit pandas openpyxl xlsxwriter

Run:
    streamlit run coffee_mt_app3.py
"""

import streamlit as st
st.title("☕ Coffee MT Converter")
st.info("Upload exclusion list → upload raw data → download cleaned file")
import pandas as pd
import re
import datetime
import io
import zipfile

# ── HS CODE CLASSIFICATION ─────────────────────────────────────────
COFFEE_HSN  = {'21011110', '21011190', '21011120', '21011130', '21011100'}
CHICORY_HSN = {'21011200', '21013010', '21012000'}

# Normalise: strip spaces, uppercase, cast to string
def normalise_hsn(val):
    return str(val).replace(' ', '').strip().upper()

def classify_hsn(val):
    h = normalise_hsn(val)
    if h in COFFEE_HSN:
        return 'Coffee'
    if h in CHICORY_HSN:
        return 'Chicory'
    return None   # everything else — drop

# ── PAGE CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Coffee MT Converter",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:opsz,wght@9..144,300;9..144,600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
    h1, h2, h3 {
        font-family: 'Fraunces', serif !important;
        font-weight: 300 !important;
        letter-spacing: -0.02em;
    }
    .main  { background-color: #faf9f6; }
    .stApp { background-color: #faf9f6; }
    .metric-card {
        background: white;
        border: 1px solid #e8e4dc;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .metric-card .value {
        font-family: 'Fraunces', serif;
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    .metric-card .label {
        font-size: 11px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
    }
    .stage-header {
        border-left: 3px solid #c8a96e;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }
    .stage-header h3 { margin: 0; color: #1a1a1a; }
    .stage-header p  { margin: 2px 0 0 0; font-size: 12px; color: #888; }
    .file-pill {
        display: inline-block;
        background: #f0ede8;
        border: 1px solid #ddd8ce;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 12px;
        margin: 3px;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e8e4dc;
        border-radius: 8px;
        background: white;
    }
    .stButton > button {
        background: #1a1a1a; color: white; border: none;
        border-radius: 6px; font-family: 'DM Mono', monospace;
        font-size: 13px; padding: 10px 24px;
    }
    .stButton > button:hover { background: #333; }
    .stDownloadButton > button {
        background: #c8a96e; color: white; border: none;
        border-radius: 6px; font-family: 'DM Mono', monospace;
        font-size: 13px; padding: 10px 24px; width: 100%;
    }
    .stDownloadButton > button:hover { background: #b8944f; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════

def load_exclusion_list(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name='Sheet1')
    df.columns = df.columns.str.strip().str.upper()
    df['KEYWORD']    = df['KEYWORD'].str.strip().str.upper()
    df['MATCH_TYPE'] = df['MATCH_TYPE'].str.strip().str.upper()
    df['HSN_FILTER'] = df['HSN_FILTER'].astype(str).str.strip().replace('NAN', '')
    return df


def apply_exclusion_list(df, exclusion_df, hsn_col):
    if 'PRODUCT DESCRIPTION' not in df.columns:
        return df, pd.DataFrame()

    desc_upper = df['PRODUCT DESCRIPTION'].astype(str).str.upper()
    hsn_upper  = df[hsn_col].astype(str).str.upper() if hsn_col and hsn_col in df.columns else None

    exclude_mask     = pd.Series(False, index=df.index)
    exclusion_reason = pd.Series('', index=df.index)

    for _, rule in exclusion_df.iterrows():
        keyword    = rule['KEYWORD']
        hsn_filter = rule['HSN_FILTER']
        reason     = rule.get('REASON', '')

        keyword_match = desc_upper.str.contains(keyword, na=False, regex=False)

        if hsn_filter and hsn_upper is not None:
            hsn_match = hsn_upper.str.contains(str(hsn_filter), na=False, regex=False)
            row_match = keyword_match & hsn_match
        else:
            row_match = keyword_match

        new_matches = row_match & ~exclude_mask
        exclusion_reason[new_matches] = f"{keyword} — {reason}"
        exclude_mask |= row_match

    excluded_df = df[exclude_mask].copy()
    excluded_df['EXCLUSION_REASON'] = exclusion_reason[exclude_mask]
    clean_df    = df[~exclude_mask].copy()
    return clean_df, excluded_df


def convert_to_mt(row):
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).strip().upper()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).strip().upper()

    if pd.isna(qty):
        return pd.Series([None, 'BLANK'])

    if unit in ('KGS', 'KG'):
        return pd.Series([round(qty / 1000, 6), 'DIRECT'])

    if unit in ('MTS', 'MT', 'MTONS'):
        return pd.Series([round(float(qty), 6), 'DIRECT'])

    if unit in ('NOS', 'CTN', 'CTNS', 'CARTONS', 'CARTON', 'PCS', 'PKGS'):
        weight_g = None
        m = re.search(r'=\s*(\d+(?:\.\d+)?)\s*KGS?\b', desc)
        if m:
            w = float(m.group(1))
            if w <= 500:
                return pd.Series([round(qty * w / 1000, 6), 'PARSED'])
            else:
                return pd.Series([round(w / 1000, 6), 'PARSED'])
        m = re.search(r'(\d+(?:\.\d+)?)\s*KG\b', desc)
        if m:
            w = float(m.group(1))
            if w <= 500:
                return pd.Series([round(qty * w / 1000, 6), 'PARSED'])
        m = re.search(r'(\d+)\s*[X*]\s*(\d+(?:\.\d+)?)\s*(?:GMS?|GRAM|G)\b', desc)
        if m:
            weight_g = float(m.group(1)) * float(m.group(2))
        if weight_g is None:
            m = re.search(r'(\d+(?:\.\d+)?)\s*(?:GMS?|GRAM|G)\b', desc)
            if m:
                candidate = float(m.group(1))
                if 1 <= candidate <= 10000:
                    weight_g = candidate
        if weight_g is not None:
            return pd.Series([round(qty * weight_g / 1_000_000, 6), 'PARSED'])
        return pd.Series([None, 'BLANK'])

    if unit in ('ML', 'MLT'):
        return pd.Series([round(qty / 1_000_000, 6), 'PARSED_ML_ASSUMED'])

    if unit in ('LTR', 'LT', 'LTRS', 'LITRE', 'LITRES'):
        return pd.Series([round(qty / 1000, 6), 'PARSED_ML_ASSUMED'])

    return pd.Series([None, 'BLANK'])


def process_file(uploaded_file, exclusion_df, hsn_col):
    """
    Reads the 'data' sheet, splits into Coffee/Chicory by HS CODE,
    applies exclusion list, then converts to MT.
    Returns dict with keys 'Coffee' and 'Chicory'.
    """
    xl  = pd.ExcelFile(uploaded_file)

    # Auto-detect sheet: prefer 'data', else first sheet
    if 'data' in xl.sheet_names:
        df_raw = xl.parse('data')
    else:
        df_raw = xl.parse(xl.sheet_names[0])

    # Normalise columns
    df_raw.columns = df_raw.columns.str.strip()

    # ── STEP 1: HSN CLASSIFICATION ─────────────────────────────────
    if hsn_col not in df_raw.columns:
        st.error(f"Column '{hsn_col}' not found. Available columns: {df_raw.columns.tolist()}")
        return {}

    df_raw['_CATEGORY'] = df_raw[hsn_col].apply(classify_hsn)

    # Count dropped rows for transparency
    dropped = df_raw['_CATEGORY'].isna().sum()
    df_relevant = df_raw[df_raw['_CATEGORY'].notna()].copy()

    results = {}
    for category in ['Coffee', 'Chicory']:
        df_cat = df_relevant[df_relevant['_CATEGORY'] == category].drop(
            columns=['_CATEGORY']
        ).reset_index(drop=True)

        if df_cat.empty:
            results[category] = {
                'original': df_cat,
                'clean': pd.DataFrame(),
                'excluded': pd.DataFrame(),
                'converted': False,
                'dropped_non_hsn': 0
            }
            continue

        original_df = df_cat.copy()

        # ── STEP 2: EXCLUSION LIST ──────────────────────────────────
        clean_df, excluded_df = apply_exclusion_list(df_cat, exclusion_df, hsn_col)

        # ── STEP 3: MT CONVERSION ───────────────────────────────────
        clean_df[['TOTAL_SOLUBLE_MT', 'MT_CONVERSION_STATUS']] = clean_df.apply(
            convert_to_mt, axis=1
        )

        results[category] = {
            'original':        original_df,
            'clean':           clean_df,
            'excluded':        excluded_df,
            'converted':       True,
            'dropped_non_hsn': dropped if category == 'Coffee' else 0  # report once
        }

    return results


def build_output_excel(results, source_filename):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        all_excluded  = []
        summary_rows  = []

        for category, data in results.items():
            if not data['converted'] or data['clean'].empty:
                continue

            clean_df    = data['clean']
            excluded_df = data['excluded']
            sheet_name  = f"{category} (2101 {'11xx' if category == 'Coffee' else '20xx'})"

            clean_df.to_excel(writer, sheet_name=sheet_name, index=False)

            if not excluded_df.empty:
                excluded_df['SOURCE_SHEET'] = sheet_name
                all_excluded.append(excluded_df)

            summary_rows.append({
                'Sheet':          sheet_name,
                'Original Rows':  len(data['original']),
                'Excluded Rows':  len(excluded_df),
                'Converted Rows': len(clean_df),
                'DIRECT':         clean_df['MT_CONVERSION_STATUS'].eq('DIRECT').sum(),
                'PARSED':         clean_df['MT_CONVERSION_STATUS'].eq('PARSED').sum(),
                'PARSED_ML':      clean_df['MT_CONVERSION_STATUS'].eq('PARSED_ML_ASSUMED').sum(),
                'BLANK':          clean_df['MT_CONVERSION_STATUS'].eq('BLANK').sum(),
                'Total MT':       round(clean_df['TOTAL_SOLUBLE_MT'].sum(), 3)
            })

        if all_excluded:
            pd.concat(all_excluded, ignore_index=True).to_excel(
                writer, sheet_name='Excluded (Audit)', index=False
            )

        if summary_rows:
            pd.DataFrame(summary_rows).to_excel(
                writer, sheet_name='Conversion Summary', index=False
            )

        # Methodology
        pd.DataFrame([
            {'Type': 'DIRECT',         'Formula': 'KGS ÷ 1,000',                    'Confidence': 'Certain'},
            {'Type': 'PARSED',         'Formula': 'NOS × per-unit weight (g) ÷ 1M', 'Confidence': 'High'},
            {'Type': 'PARSED_ML',      'Formula': 'ML ÷ 1M  or  LTR ÷ 1,000',       'Confidence': 'Approximate'},
            {'Type': 'BLANK',          'Formula': 'Not converted',                   'Confidence': 'N/A'},
        ]).to_excel(writer, sheet_name='Methodology', index=False)

    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ☕ Coffee MT Converter")
    st.markdown("---")
    st.markdown("""
**Pipeline**
1. Upload exclusion list
2. Upload raw file(s)
3. Review cleaning & conversion
4. Download outputs

---
**Coffee HS Codes**
- 21011110, 21011190
- 21011120, 21011130

**Chicory HS Codes**
- 21011200, 21013010

---
**Conversion types**
- `DIRECT` — KGS ÷ 1,000
- `PARSED` — NOS × weight
- `PARSED_ML` — ML ÷ 1,000,000
- `BLANK` — unresolvable
    """)
    st.markdown("---")
    st.caption(f"v3.0 · Built for SIP LDC · {datetime.date.today().strftime('%b %Y')}")


st.markdown("# Coffee Export MT Conversion")
st.markdown("Reads raw export data, splits by HS code, excludes noise, converts to MT.")
st.markdown("---")


# ── STAGE 1: EXCLUSION LIST ────────────────────────────────────────
st.markdown("""
<div class="stage-header">
    <h3>Stage 1 — Exclusion List</h3>
    <p>Upload your keyword exclusion list. Applied after HSN filtering.</p>
</div>
""", unsafe_allow_html=True)

excl_file = st.file_uploader(
    "Upload exclusion_list.xlsx",
    type=['xlsx'],
    key='excl_uploader'
)

exclusion_df = None
if excl_file:
    try:
        exclusion_df = load_exclusion_list(excl_file)
        col1, col2 = st.columns([1, 3])
        with col1:
            st.success(f"✅ {len(exclusion_df)} rules loaded")
        with col2:
            with st.expander("Preview exclusion rules"):
                st.dataframe(exclusion_df, use_container_width=True, height=200)
    except Exception as e:
        st.error(f"Error reading exclusion list: {e}")

st.markdown("---")


# ── STAGE 2: DATA FILES ────────────────────────────────────────────
st.markdown("""
<div class="stage-header">
    <h3>Stage 2 — Upload Raw Data Files</h3>
    <p>Upload one or multiple monthly ALL_PORT files. Each must have a 'data' sheet.</p>
</div>
""", unsafe_allow_html=True)

if exclusion_df is None:
    st.info("⬆️ Please upload the exclusion list first.")
else:
    hsn_col = st.text_input(
        "HSN column name in your data files",
        value="HS CODE",
        help="Exact column header containing HS codes like 21011110"
    )

    data_files = st.file_uploader(
        "Upload raw Excel file(s)",
        type=['xlsx'],
        accept_multiple_files=True,
        key='data_uploader'
    )

    if data_files:
        st.markdown(f"**{len(data_files)} file(s) uploaded:**")
        for f in data_files:
            st.markdown(f'<span class="file-pill">📄 {f.name}</span>', unsafe_allow_html=True)
        st.markdown("")

        run_btn = st.button("▶ Run Pipeline", type="primary")

        if run_btn:
            st.markdown("---")
            st.markdown("""
<div class="stage-header">
    <h3>Stage 3 — Results</h3>
    <p>Cleaning and conversion results for each file.</p>
</div>
""", unsafe_allow_html=True)

            all_outputs    = {}
            master_coffee  = []
            master_chicory = []
            master_log     = []

            progress = st.progress(0, text="Processing files...")

            for i, uploaded_file in enumerate(data_files):
                fname = uploaded_file.name
                progress.progress(i / len(data_files), text=f"Processing {fname}...")

                try:
                    results = process_file(uploaded_file, exclusion_df, hsn_col)
                    if not results:
                        continue

                    output_buf = build_output_excel(results, fname)
                    all_outputs[fname] = output_buf

                    # Accumulate master
                    for category, data in results.items():
                        if data['converted'] and not data['clean'].empty:
                            data['clean']['SOURCE_FILE'] = fname
                            if category == 'Coffee':
                                master_coffee.append(data['clean'])
                            else:
                                master_chicory.append(data['clean'])

                    # Log row
                    total_orig = sum(len(d['original']) for d in results.values() if d['converted'])
                    total_excl = sum(len(d['excluded']) for d in results.values() if d['converted'])
                    total_mt   = sum(
                        d['clean']['TOTAL_SOLUBLE_MT'].sum()
                        for d in results.values()
                        if d['converted'] and not d['clean'].empty
                    )
                    master_log.append({
                        'File':          fname,
                        'Original Rows': total_orig,
                        'Excluded':      total_excl,
                        'Total MT':      round(total_mt, 3)
                    })

                    # Per-file card
                    with st.expander(f"📄 {fname}", expanded=(len(data_files) == 1)):

                        for category, data in results.items():
                            if not data['converted']:
                                continue
                            c         = data['clean']
                            excl_count = len(data['excluded'])
                            mt_total   = c['TOTAL_SOLUBLE_MT'].sum() if not c.empty else 0

                            st.markdown(f"**{category}**")
                            sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
                            sc1.metric("Rows In",   len(data['original']))
                            sc2.metric("Excluded",  excl_count)
                            sc3.metric("DIRECT",    int(c['MT_CONVERSION_STATUS'].eq('DIRECT').sum()) if not c.empty else 0)
                            sc4.metric("PARSED",    int(c['MT_CONVERSION_STATUS'].eq('PARSED').sum()) if not c.empty else 0)
                            sc5.metric("BLANK",     int(c['MT_CONVERSION_STATUS'].eq('BLANK').sum()) if not c.empty else 0)
                            sc6.metric("Total MT",  f"{mt_total:,.3f}")

                            if excl_count > 0:
                                with st.expander(f"  ⚠️ {excl_count} excluded rows from {category}"):
                                    cols_to_show = [col for col in ['PRODUCT DESCRIPTION', 'HS CODE', 'STANDARD QUANTITY', 'EXCLUSION_REASON'] if col in data['excluded'].columns]
                                    st.dataframe(
                                        data['excluded'][cols_to_show],
                                        use_container_width=True,
                                        height=200
                                    )

                        st.download_button(
                            label=f"⬇ Download {fname.replace('ALL_PORT_ALL_E_', 'MT_FINAL_')}",
                            data=output_buf,
                            file_name=fname.replace('ALL_PORT_ALL_E_', 'MT_FINAL_'),
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            key=f"dl_{fname}"
                        )

                except Exception as e:
                    st.error(f"❌ Error processing {fname}: {e}")
                    import traceback
                    st.code(traceback.format_exc())

            progress.progress(1.0, text="✅ All files processed!")

            # ── BATCH SUMMARY ──────────────────────────────────────
            if len(data_files) > 1 and master_log:
                st.markdown("---")
                st.markdown("""
<div class="stage-header">
    <h3>Batch Summary</h3>
    <p>Aggregated results across all processed files.</p>
</div>
""", unsafe_allow_html=True)

                log_df = pd.DataFrame(master_log)
                totals = log_df[['Original Rows', 'Excluded', 'Total MT']].sum()
                t1, t2, t3 = st.columns(3)
                t1.metric("Total Rows",     int(totals['Original Rows']))
                t2.metric("Total Excluded", int(totals['Excluded']))
                t3.metric("Grand Total MT", f"{totals['Total MT']:,.1f}")

                st.dataframe(log_df, use_container_width=True)

                master_buf = io.BytesIO()
                with pd.ExcelWriter(master_buf, engine='openpyxl') as writer:
                    log_df.to_excel(writer, sheet_name='Conversion Log', index=False)
                    if master_coffee:
                        pd.concat(master_coffee, ignore_index=True).to_excel(
                            writer, sheet_name='All Coffee Combined', index=False
                        )
                    if master_chicory:
                        pd.concat(master_chicory, ignore_index=True).to_excel(
                            writer, sheet_name='All Chicory Combined', index=False
                        )
                master_buf.seek(0)

                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for fname, buf in all_outputs.items():
                        buf.seek(0)
                        zf.writestr(fname.replace('ALL_PORT_ALL_E_', 'MT_FINAL_'), buf.read())
                    master_buf.seek(0)
                    zf.writestr('MASTER_MT_SUMMARY.xlsx', master_buf.read())
                zip_buf.seek(0)

                col_a, col_b = st.columns(2)
                with col_a:
                    master_buf.seek(0)
                    st.download_button(
                        label="⬇ Download Master Summary (Excel)",
                        data=master_buf,
                        file_name=f"MASTER_MT_SUMMARY_{datetime.date.today()}.xlsx",
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                with col_b:
                    st.download_button(
                        label="⬇ Download All Files (ZIP)",
                        data=zip_buf,
                        file_name=f"MT_CONVERTED_ALL_{datetime.date.today()}.zip",
                        mime='application/zip'
                    )
