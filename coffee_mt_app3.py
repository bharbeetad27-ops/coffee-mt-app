import streamlit as st
import pandas as pd
import io
import re
from openpyxl import load_workbook
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
.hero h1 { font-size: 42px; font-weight: 600; }
.hero p  { color: #94a3b8; }
.section {
    background: #f8fafc;
    padding: 40px;
    border-radius: 16px;
    margin-bottom: 40px;
}
.feature-grid { display: flex; gap: 20px; flex-wrap: wrap; }
.feature {
    position: relative;
    flex: 1;
    min-width: 250px;
    height: 200px;
    border-radius: 12px;
    overflow: hidden;
}
.feature img { width: 100%; height: 100%; object-fit: cover; }
.feature .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.85), rgba(0,0,0,0.2));
    display: flex;
    align-items: flex-end;
    padding: 20px;
}
.feature h3 { color: white; margin: 0; }
.feature p  { color: #cbd5f5; font-size: 13px; }
.pipeline   { padding: 20px; }
.block {
    background: #0f172a;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.stButton button {
    background: #1d4ed8;
    color: white;
    border-radius: 8px;
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
    <div class="overlay"><div>
        <h3>High Volume Processing</h3>
        <p>Handle large export datasets efficiently</p>
    </div></div>
</div>

<div class="feature">
    <img src="https://images.unsplash.com/photo-1509042239860-f550ce710b93">
    <div class="overlay"><div>
        <h3>Smart Classification</h3>
        <p>Coffee & Chicory separation using HSN codes</p>
    </div></div>
</div>

<div class="feature">
    <img src="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085">
    <div class="overlay"><div>
        <h3>Accurate MT Conversion</h3>
        <p>Reliable conversion across formats</p>
    </div></div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

# ================================================================
# CONSTANTS
# ================================================================

COFFEE_CODES  = [21011110, 21011120, 21011130, 21011190, 21011200]
CHICORY_CODES = [210130, 21013010]
ALL_CODES     = COFFEE_CODES + CHICORY_CODES

STRICT_COFFEE_CHECK_CODES = [21011190, 21011200]

COFFEE_SIGNALS = [
    'COFFEE', 'KAPPI', 'CAPPI', 'COFFE', 'COFEE',
    'CAPPUCCINO', 'CAPUCCINO', 'CAPUCHINO',
    'CPC', 'LATTE', 'ESPRESSO', 'AMERICANO', 'MOCHA',
    'MACCHIATO', 'FRAPPE', 'COLD BREW', 'COLD COFFEE',
    'NESCAFE', 'NESCAFÉ', 'BRU', 'LEVISTA', 'DAVIDOFF',
    'COTHAS', 'CONTINENTAL', 'CHAIZUP',
    'TATA COFFEE', 'CAFÉ', 'CAFE',
    'SPRAY DRIED', 'FREEZE DRIED', 'AGGLOMERATED',
    'DECOCTION', 'PERCOLATE', 'ROAST AND GROUND', 'CHICORY'
]

WEAK_COFFEE_SIGNALS = [
    'PREMIX', 'PRE-MIX', '3 IN 1', '2 IN 1',
    'SACHET', 'MIX', 'VENDING MIX'
]

TEA_SIGNALS = [
    'TEA', 'GREEN TEA', 'BLACK TEA',
    'MASALA TEA', 'CHAI', 'LEMON TEA', 'ICED TEA'
]

# Pre-compiled regex patterns for speed
KG_MULTI_PATTERN = re.compile(r'([\d.]+)\s*KG\s*X\s*([\d.]+)', re.IGNORECASE)  # e.g. 1 KG X 16
MULTI_G_PATTERN  = re.compile(r'([\d.]+)\s*X\s*([\d.]+)\s*G',  re.IGNORECASE)  # e.g. 6X180G
SINGLE_G_PATTERN = re.compile(r'([\d.]+)\s*G',                  re.IGNORECASE)  # e.g. 45G fallback

# ================================================================
# FUNCTIONS
# ================================================================

def should_exclude(desc, hsn, excl_df):
    desc = str(desc).upper()
    hsn  = int(hsn) if pd.notna(hsn) else 0

    if hsn in STRICT_COFFEE_CHECK_CODES:
        strong = any(s in desc for s in COFFEE_SIGNALS)
        weak   = any(s in desc for s in WEAK_COFFEE_SIGNALS)
        tea    = any(s in desc for s in TEA_SIGNALS)

        if strong:
            return False, ''
        elif tea:
            return True, "Tea detected"
        elif weak:
            return False, "Premix assumed coffee"
        else:
            return True, "No coffee signal"

    for _, r in excl_df.iterrows():
        if r['MATCH_TYPE'] == "CONTAINS" and r['KEYWORD'] in desc:
            return True, r['REASON']

    return False, ''


def convert_to_mt(row):
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()

    if pd.isna(qty):
        return None, 'BLANK'

    try:
        qty = float(qty)
    except (TypeError, ValueError):
        return None, 'BLANK'

    if unit in ('KGS', 'KG'):
        return qty / 1000, 'DIRECT'

    if unit in ('MTS', 'MT'):
        return qty, 'DIRECT'

    if unit in ('ML', 'MLT'):
        return qty / 1_000_000, 'DIRECT'

    if unit in ('NOS', 'PCS', 'CTN'):
        try:
            # Pattern 1: "1 KG X 16 NOS" → each unit is 1 KG
            m = KG_MULTI_PATTERN.search(desc)
            if m:
                kg_each = float(m.group(1))
                return qty * kg_each / 1000, 'PARSED'

            # Pattern 2: "6X180G" or "36X24G" → multiplier x grams
            m = MULTI_G_PATTERN.search(desc)
            if m:
                multiplier = float(m.group(1))
                grams_each = float(m.group(2))
                return qty * multiplier * grams_each / 1_000_000, 'PARSED'

            # Pattern 3: fallback "45G" → single gram weight
            m = SINGLE_G_PATTERN.search(desc)
            if m:
                return qty * float(m.group(1)) / 1_000_000, 'PARSED'

        except (TypeError, ValueError):
            return None, 'BLANK'

    return None, 'BLANK'


@st.cache_data
def load_exclusion_list(file):
    return pd.read_excel(file)


@st.cache_data
def load_raw_file(file):
    return pd.read_excel(file)


def process_file(file, excl_df):
    df     = load_raw_file(file)
    hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)
    df     = df[df[hs_col].isin(ALL_CODES)].copy()

    # Vectorized exclusion (faster than iterrows)
    results       = df.apply(lambda r: should_exclude(r['PRODUCT DESCRIPTION'], r[hs_col], excl_df), axis=1)
    df['_excl']   = [x[0] for x in results]
    df['_reason'] = [x[1] for x in results]

    removed           = df[df['_excl']].copy()
    removed['REASON'] = removed['_reason']
    keep              = df[~df['_excl']].copy()

    for col in ['_excl', '_reason']:
        removed.drop(columns=[col], inplace=True, errors='ignore')
        keep.drop(columns=[col], inplace=True, errors='ignore')

    coffee  = keep[keep[hs_col].isin(COFFEE_CODES)].copy()
    chicory = keep[keep[hs_col].isin(CHICORY_CODES)].copy()

    for d in [coffee, chicory]:
        if len(d):
            mt_results  = d.apply(convert_to_mt, axis=1)
            d['MT']     = [x[0] for x in mt_results]
            d['STATUS'] = [x[1] for x in mt_results]

    return coffee, chicory, removed


def apply_header_colours(buf):
    buf.seek(0)
    wb = load_workbook(buf)

    blue_fill  = PatternFill("solid", fgColor="1D4ED8")
    green_fill = PatternFill("solid", fgColor="15803D")
    white_font = Font(color="FFFFFF", bold=True)
    center     = Alignment(horizontal="center")

    for cell in wb["Coffee"][1]:
        cell.fill      = blue_fill
        cell.font      = white_font
        cell.alignment = center

    for cell in wb["Chicory"][1]:
        cell.fill      = green_fill
        cell.font      = white_font
        cell.alignment = center

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out

# ================================================================
# PIPELINE UI
# ================================================================

st.markdown('<div class="pipeline">', unsafe_allow_html=True)

st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("Stage 1 — Upload Exclusion List")
excl = st.file_uploader("Exclusion List", type=["xlsx"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("Stage 2 — Upload Raw Data")
raws = st.file_uploader("Raw CYBEX Files", type=["xlsx"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.button("Run"):
    if not excl:
        st.error("Please upload an exclusion list.")
    elif not raws:
        st.error("Please upload at least one raw file.")
    else:
        excl_df = load_exclusion_list(excl)

        for f in raws:
            with st.spinner(f"Processing {f.name}..."):
                c, ch, e = process_file(f, excl_df)

                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as w:
                    c.to_excel(w,  sheet_name="Coffee",   index=False)
                    ch.to_excel(w, sheet_name="Chicory",  index=False)
                    e.to_excel(w,  sheet_name="Excluded", index=False)

                # Apply colours AFTER ExcelWriter closes
                final_buf = apply_header_colours(buf)

            st.download_button(
                label=f"Download {f.name}",
                data=final_buf,
                file_name=f"MT_CLEANED_{f.name}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.markdown('</div>', unsafe_allow_html=True)
