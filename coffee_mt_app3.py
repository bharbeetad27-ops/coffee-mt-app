import streamlit as st
import pandas as pd
import io
import re
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Coffee Trade Intelligence", layout="wide")

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #020617 0%, #020617 100%);
    color: white;
    font-family: 'Inter', sans-serif;
}
.hero {
    background-image: linear-gradient(rgba(2,6,23,0.75), rgba(2,6,23,0.95)),
                      url("https://images.unsplash.com/photo-1498804103079-a6351b050096");
    background-size: cover;
    background-position: center;
    padding: 80px 40px;
    border-radius: 16px;
    margin-bottom: 40px;
}
.hero h1 { font-size: 42px; font-weight: 600; margin-bottom: 10px; }
.hero p { color: #94a3b8; font-size: 16px; }
.section { background: #f8fafc; padding: 40px; border-radius: 16px; margin-bottom: 40px; }
.feature-grid { display: flex; gap: 20px; flex-wrap: wrap; }
.feature { position: relative; flex: 1; min-width: 250px; height: 200px; border-radius: 12px; overflow: hidden; }
.feature img { width: 100%; height: 100%; object-fit: cover; }
.feature .overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.85), rgba(0,0,0,0.2));
    display: flex; align-items: flex-end; padding: 20px;
}
.feature h3 { color: white; margin: 0; font-size: 18px; }
.feature p { color: #cbd5f5; font-size: 13px; }
.pipeline { padding: 20px; }
.block { background: #0f172a; padding: 25px; border-radius: 12px; margin-bottom: 20px; }
.block h3 { color: white; }
.stFileUploader { background: #020617 !important; border-radius: 10px; }
.stButton button { background: #1d4ed8; color: white; border-radius: 8px; }
@media (max-width: 768px) {
    .hero { padding: 40px 20px; }
    .hero h1 { font-size: 28px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <h1>Coffee Trade Intelligence</h1>
    <p>Upload → Clean → Convert → Download</p>
</div>
""", unsafe_allow_html=True)

# ---------------- FEATURES ----------------
st.markdown("""
<div class="section">
<h2 style="color:#0f172a;">Trade Data Capabilities</h2>
<div class="feature-grid">
<div class="feature">
    <img src="https://images.unsplash.com/photo-1511920170033-f8396924c348">
    <div class="overlay"><div><h3>High Volume Processing</h3><p>Handle large export datasets efficiently</p></div></div>
</div>
<div class="feature">
    <img src="https://images.unsplash.com/photo-1509042239860-f550ce710b93">
    <div class="overlay"><div><h3>Smart Classification</h3><p>Coffee & Chicory separation using HSN codes</p></div></div>
</div>
<div class="feature">
    <img src="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085">
    <div class="overlay"><div><h3>Accurate MT Conversion</h3><p>Reliable conversion across formats</p></div></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ================================================================
# CORE LOGIC (from notebook)
# ================================================================

# ── HSN CODES ────────────────────────────────────────────────────
COFFEE_CODES  = [21011110, 21011120, 21011130, 21011190, 21011200]
CHICORY_CODES = [210130, 21013010]
ALL_CODES     = COFFEE_CODES + CHICORY_CODES

# ── STYLING ──────────────────────────────────────────────────────
COFFEE_HDR  = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
CHICORY_HDR = PatternFill(start_color='375623', end_color='375623', fill_type='solid')
REMOVED_HDR = PatternFill(start_color='7B0000', end_color='7B0000', fill_type='solid')
ALT_BLUE    = PatternFill(start_color='DDEEFF', end_color='DDEEFF', fill_type='solid')
ALT_GREEN   = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
ALT_RED     = PatternFill(start_color='FFE0E0', end_color='FFE0E0', fill_type='solid')
HDR_FONT    = Font(color='FFFFFF', bold=True)


def style_sheet(ws, hdr_fill, row_fill):
    for cell in ws[1]:
        cell.fill = hdr_fill
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal='center', wrap_text=True)
    for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
        for cell in row:
            cell.fill = row_fill if i % 2 == 0 else PatternFill(fill_type=None)
    for col in ws.columns:
        w = max((len(str(c.value or '')) for c in col), default=10)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(w + 2, 40)


def load_exclusion_rules(excl_file):
    """Load exclusion rules from uploaded Excel file."""
    excl_df = pd.read_excel(excl_file)
    excl_df['KEYWORD']    = excl_df['KEYWORD'].astype(str).str.upper().str.strip()
    excl_df['HSN_FILTER'] = excl_df['HSN_FILTER'].astype(str).str.strip().replace('nan', '')
    return excl_df


def should_exclude(description, hsn_code, excl_df):
    """Returns (True, reason) if row should be removed, else (False, '')."""
    desc = str(description).upper().strip()
    hsn  = str(int(hsn_code)) if pd.notna(hsn_code) else ''

    COFFEE_GUARD = [
        'SOLUBLE COFFEE', 'INSTANT COFFEE', 'SPRAY DRIED COFFEE',
        'FREEZE DRIED COFFEE', 'COFFEE EXTRACT', 'COFFEE PREMIX',
        'FILTER COFFEE', 'COFFEE CHICORY', 'NESCAFE', 'DAVIDOFF',
        'LEVISTA', 'CONTINENTAL COFFEE', 'COTHAS', 'BRU GOLD',
        'BRU SELECT', 'CHAIZUP'
    ]
    if any(g in desc for g in COFFEE_GUARD):
        return False, ''

    for _, rule in excl_df.iterrows():
        kw         = rule['KEYWORD']
        hsn_filter = rule['HSN_FILTER']
        if hsn_filter and hsn_filter != hsn:
            continue
        if rule['MATCH_TYPE'] == 'CONTAINS' and kw in desc:
            return True, rule['REASON']
        elif rule['MATCH_TYPE'] == 'EXACT' and kw == desc:
            return True, rule['REASON']

    return False, ''


def convert_to_mt(row):
    """Convert STANDARD QUANTITY to Metric Tons."""
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).strip().upper()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).strip().upper()

    if pd.isna(qty):
        return None, 'BLANK'

    # DIRECT — KGS
    if unit in ('KGS', 'KG'):
        return round(float(qty) / 1000, 6), 'DIRECT'

    # DIRECT — MTS
    if unit in ('MTS', 'MT', 'MTONS'):
        return round(float(qty), 6), 'DIRECT'

    # COUNT UNITS — parse from description
    if unit in ('NOS', 'CTN', 'CTNS', 'CARTONS', 'CARTON', 'PCS', 'PKGS', 'UNT', 'BOX', 'CAN', 'CTM'):
        weight_g = None

        # NET WT: X.XXX KGS
        match = re.search(r'NET\s*\.?\s*WT\s*[:\s]+([\d.]+)\s*KGS?\b', desc)
        if match:
            wkg = float(match.group(1))
            if wkg <= 500:
                return round(float(qty) * wkg / 1000, 6), 'PARSED'

        # = X KGS per carton
        match = re.search(r'=\s*([\d.]+)\s*KGS?\b', desc)
        if match:
            wkg = float(match.group(1))
            if wkg <= 500:
                return round(float(qty) * wkg / 1000, 6), 'PARSED'
            else:
                return round(wkg / 1000, 6), 'PARSED'

        # X KGS x N PCS (e.g. "0.2 KGS X 12 PCS")
        match = re.search(r'([\d.]+)\s*KGS?\s*[X*×]\s*(\d+)', desc)
        if match:
            wkg, count = float(match.group(1)), float(match.group(2))
            if wkg <= 500:
                return round(float(qty) * wkg * count / 1000, 6), 'PARSED'

        # N KG standalone
        match = re.search(r'([\d.]+)\s*KG\b', desc)
        if match:
            wkg = float(match.group(1))
            if wkg <= 500:
                return round(float(qty) * wkg / 1000, 6), 'PARSED'

        # NxWeightG with double-X  e.g. "144XX0.9G", "24X100G"
        match = re.search(r'(\d+)\s*[X*×]{1,2}\s*([\d.]+)\s*(?:GMS?|GRAM(?:S)?|G)\b', desc)
        if match:
            weight_g = float(match.group(1)) * float(match.group(2))

        # WeightG x N  e.g. "200GMX60PKTS"
        if weight_g is None:
            match = re.search(r'([\d.]+)\s*(?:GMS?|GRAM(?:S)?|G)\s*[X*×]{1,2}\s*(\d+)', desc)
            if match:
                weight_g = float(match.group(1)) * float(match.group(2))

        # X GRAMS EACH  e.g. "50 GRAMS EACH TIN"
        if weight_g is None:
            match = re.search(r'([\d.]+)\s*GRAMS?\s*EACH', desc)
            if match:
                weight_g = float(match.group(1))

        # Single standalone grams
        if weight_g is None:
            match = re.search(r'([\d.]+)\s*(?:GMS?|GRAM(?:S)?|G)\b', desc)
            if match:
                candidate = float(match.group(1))
                if 1 <= candidate <= 10000:
                    weight_g = candidate

        if weight_g is not None:
            return round(float(qty) * weight_g / 1_000_000, 6), 'PARSED'

        return None, 'BLANK'

    # ML / LTR — density assumed 1g/ml
    if unit in ('ML', 'MLT'):
        return round(float(qty) / 1_000_000, 6), 'PARSED_ML_ASSUMED'
    if unit in ('LTR', 'LT', 'LTRS', 'LITRE', 'LITRES'):
        return round(float(qty) / 1000, 6), 'PARSED_ML_ASSUMED'

    return None, 'BLANK'


def process_file(raw_file, excl_df):
    """Full pipeline: HSN filter → exclusion filter → split → MT convert."""
    df = pd.read_excel(raw_file)

    # Find HS CODE column
    hs_col = next((c for c in df.columns if str(c).upper().strip() == 'HS CODE'), None)
    if not hs_col:
        hs_col = next((c for c in df.columns
                       if 'HS' in str(c).upper() and 'CODE' in str(c).upper()
                       and '2 ' not in str(c) and '4 ' not in str(c) and '6 ' not in str(c)), None)
    if not hs_col:
        return None, f"No HS CODE column found. Columns: {df.columns.tolist()}"

    # STEP 1 — HSN filter
    df[hs_col] = pd.to_numeric(df[hs_col], errors='coerce')
    df_hsn = df[df[hs_col].isin(ALL_CODES)].copy().reset_index(drop=True)

    if len(df_hsn) == 0:
        return None, "No matching HSN rows found."

    # STEP 2 — Exclusion list filter
    desc_col    = 'PRODUCT DESCRIPTION'
    removed_rows = []
    keep_mask    = []

    if desc_col in df_hsn.columns:
        for _, row in df_hsn.iterrows():
            exclude, reason = should_exclude(row[desc_col], row[hs_col], excl_df)
            if exclude:
                row_copy = row.copy()
                row_copy['EXCLUSION_REASON'] = reason
                removed_rows.append(row_copy)
                keep_mask.append(False)
            else:
                keep_mask.append(True)
        df_kept = df_hsn[keep_mask].copy().reset_index(drop=True)
        df_excl = pd.DataFrame(removed_rows)
    else:
        df_kept = df_hsn.copy()
        df_excl = pd.DataFrame()

    # STEP 3 — Split Coffee / Chicory
    df_coffee  = df_kept[df_kept[hs_col].isin(COFFEE_CODES)].copy().reset_index(drop=True)
    df_chicory = df_kept[df_kept[hs_col].isin(CHICORY_CODES)].copy().reset_index(drop=True)

    # STEP 4 — MT conversion on both sheets
    for df_part in [df_coffee, df_chicory]:
        if len(df_part) > 0:
            mt_vals, mt_status = zip(*df_part.apply(convert_to_mt, axis=1))
            df_part['TOTAL_SOLUBLE_MT']     = mt_vals
            df_part['MT_CONVERSION_STATUS'] = mt_status

    stats = {
        'raw_rows'     : len(df),
        'hsn_matched'  : len(df_hsn),
        'excluded'     : len(removed_rows),
        'coffee_rows'  : len(df_coffee),
        'chicory_rows' : len(df_chicory),
        'coffee_mt'    : round(df_coffee['TOTAL_SOLUBLE_MT'].sum(skipna=True), 3) if len(df_coffee) > 0 else 0,
        'chicory_mt'   : round(df_chicory['TOTAL_SOLUBLE_MT'].sum(skipna=True), 3) if len(df_chicory) > 0 else 0,
        'coffee_direct': int((df_coffee['MT_CONVERSION_STATUS'] == 'DIRECT').sum()) if len(df_coffee) > 0 else 0,
        'coffee_parsed': int(df_coffee['MT_CONVERSION_STATUS'].str.startswith('PARSED', na=False).sum()) if len(df_coffee) > 0 else 0,
        'coffee_blank' : int((df_coffee['MT_CONVERSION_STATUS'] == 'BLANK').sum()) if len(df_coffee) > 0 else 0,
    }

    return (df_coffee, df_chicory, df_excl, stats), None


def build_excel_output(df_coffee, df_chicory, df_excl):
    """Write all sheets to an in-memory xlsx buffer."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:

        df_coffee.to_excel(writer, sheet_name='Coffee (2101 11xx)', index=False)
        style_sheet(writer.sheets['Coffee (2101 11xx)'], COFFEE_HDR, ALT_BLUE)

        if len(df_chicory) > 0:
            df_chicory.to_excel(writer, sheet_name='Chicory (2101 20xx)', index=False)
        else:
            pd.DataFrame(columns=df_coffee.columns).to_excel(
                writer, sheet_name='Chicory (2101 20xx)', index=False)
        style_sheet(writer.sheets['Chicory (2101 20xx)'], CHICORY_HDR, ALT_GREEN)

        if len(df_excl) > 0:
            df_excl.to_excel(writer, sheet_name='Excluded (Audit)', index=False)
            style_sheet(writer.sheets['Excluded (Audit)'], REMOVED_HDR, ALT_RED)

    buf.seek(0)
    return buf


# ================================================================
# UI — PIPELINE
# ================================================================

st.markdown('<div class="pipeline">', unsafe_allow_html=True)

st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("Stage 1 — Upload Exclusion List")
exclusion_file = st.file_uploader("Upload Excel file", type=["xlsx"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("Stage 2 — Upload Raw Data")
raw_files = st.file_uploader("Upload raw files", type=["xlsx"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

run = st.button("Run Pipeline")

if run:
    if not exclusion_file or not raw_files:
        st.error("Please upload both the exclusion list and at least one raw data file.")
    else:
        st.success("Processing started...")

        excl_df = load_exclusion_rules(exclusion_file)
        st.info(f"Loaded {len(excl_df)} exclusion rules.")

        all_results   = []
        combined_buf  = None

        for raw_file in raw_files:
            fname = raw_file.name
            st.write(f"**Processing:** `{fname}`")

            result, err = process_file(raw_file, excl_df)

            if err:
                st.error(f"{fname}: {err}")
                continue

            df_coffee, df_chicory, df_excl, stats = result
            all_results.append({'file': fname, **stats})

            # Per-file download
            file_buf = build_excel_output(df_coffee, df_chicory, df_excl)
            out_name = 'CLEANED_MT_' + fname
            st.download_button(
                label=f"⬇ Download {out_name}",
                data=file_buf,
                file_name=out_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key=f"dl_{fname}"
            )

        # ── SUMMARY ──────────────────────────────────────────────────
        if all_results:
            st.markdown("---")
            st.subheader("Batch Summary")

            summary_df = pd.DataFrame(all_results)

            total_coffee_mt  = summary_df['coffee_mt'].sum()
            total_chicory_mt = summary_df['chicory_mt'].sum()
            total_coffee     = summary_df['coffee_rows'].sum()
            total_chicory    = summary_df['chicory_rows'].sum()
            total_excluded   = summary_df['excluded'].sum()
            total_blank      = summary_df['coffee_blank'].sum()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Coffee Rows",   f"{total_coffee:,}")
            col2.metric("Chicory Rows",  f"{total_chicory:,}")
            col3.metric("Coffee MT",     f"{total_coffee_mt:.3f}")
            col4.metric("Chicory MT",    f"{total_chicory_mt:.3f}")

            col5, col6 = st.columns(2)
            col5.metric("Excluded Rows", f"{total_excluded:,}")
            col6.metric("Unresolved (BLANK)", f"{total_blank:,}")

            st.dataframe(summary_df, use_container_width=True)

            # Summary Excel download
            sum_buf = io.BytesIO()
            with pd.ExcelWriter(sum_buf, engine='openpyxl') as writer:
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            sum_buf.seek(0)
            st.download_button(
                label="⬇ Download Batch Summary",
                data=sum_buf,
                file_name="MT_Conversion_Summary.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key="dl_summary"
            )

st.markdown('</div>', unsafe_allow_html=True)
