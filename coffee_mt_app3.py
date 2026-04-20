import streamlit as st
import pandas as pd
import io
import re
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment

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
.hero p { color: #94a3b8; }
.pipeline { padding: 20px; }
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

# ================================================================
# CONSTANTS
# ================================================================
COFFEE_CODES = [21011110, 21011120, 21011130, 21011190, 21011200]
CHICORY_CODES = [21013010, 21013090]

CANDIDATE_CODES = [
    9019090, 9019020, 9019010, 9012190, 9012290,
    9011119, 9011129,
    21039040, 21012090, 21069099
]

ALL_CODES = COFFEE_CODES + CHICORY_CODES + CANDIDATE_CODES
STRICT_COFFEE_CHECK_CODES = [21011190, 21011200]

COFFEE_SIGNALS = [
    'COFFEE', 'KAPPI', 'CAPPI', 'COFFE', 'COFEE',
    'CAPPUCCINO', 'LATTE', 'ESPRESSO',
    'NESCAFE', 'BRU', 'LEVISTA', 'DAVIDOFF',
    'CAFÉ', 'CAFE'
]

WEAK_COFFEE_SIGNALS = [
    'PREMIX', 'PRE-MIX', '3 IN 1', '2 IN 1',
    'SACHET', 'MIX', 'VENDING MIX'
]

TEA_SIGNALS = [
    'TEA', 'GREEN TEA', 'BLACK TEA',
    'MASALA TEA', 'CHAI'
]

TRUE_SOLUBLE_SIGNALS = [
    'INSTANT', 'SOLUBLE', 'AGGLOMERATED',
    'SPRAY DRIED', 'FREEZE DRIED'
]

RAW_BEAN_SIGNALS = [
    'NOT ROASTED', 'GREEN BEAN', 'ARABICA',
    'ROBUSTA', 'CHERRY', 'PLANTATION'
]

HARD_EXCLUDE_SIGNALS = [
    'CHUKKU',
    'SUKKU',
    'MALLI',
    'GINGER COFFEE',
    'HERBAL EXTRACT'
]

# ================================================================
# EXCLUSION LOGIC
# ================================================================
def should_exclude(desc, hsn, excl_df):
    desc = str(desc).upper()

    try:
        hsn = int(hsn) if pd.notna(hsn) else 0
    except:
        hsn = 0

    # Hard exclusion first
    if any(x in desc for x in HARD_EXCLUDE_SIGNALS):
        return True, 'Hard excluded'

    # Exclusion list second
    for _, r in excl_df.iterrows():
        if r['MATCH_TYPE'] == 'CONTAINS' and r['KEYWORD'] in desc:
            return True, r['REASON']

    # Allow chicory codes
    if hsn in CHICORY_CODES:
        return False, ''

    # Strict coffee validation
    if hsn in STRICT_COFFEE_CHECK_CODES:
        strong = any(s in desc for s in COFFEE_SIGNALS)
        weak = any(s in desc for s in WEAK_COFFEE_SIGNALS)
        tea = any(s in desc for s in TEA_SIGNALS)

        if any(s in desc for s in TRUE_SOLUBLE_SIGNALS):
            return False, ''

        if strong:
            return False, ''
        elif tea:
            return True, 'Tea detected'
        elif weak:
            return False, 'Premix assumed coffee'
        else:
            return True, 'No coffee signal'

    return False, ''

# ================================================================
# CANDIDATE CLASSIFIER
# ================================================================
def classify_candidate(desc):
    desc = str(desc).upper()

    if any(x in desc for x in HARD_EXCLUDE_SIGNALS):
        return 'EXCLUDE'

    if any(r in desc for r in RAW_BEAN_SIGNALS):
        return 'EXCLUDE'

    if 'TEA PREMIX' in desc and 'COFFEE' in desc:
        return 'EXCLUDE'

    if 'CHICORY' in desc:
        return 'CHICORY'

    if any(s in desc for s in TRUE_SOLUBLE_SIGNALS):
        return 'COFFEE'

    if any(s in desc for s in COFFEE_SIGNALS):
        return 'COFFEE'

    return 'EXCLUDE'

# ================================================================
# MT CONVERSION (UNCHANGED)
# ================================================================
def convert_to_mt(row):
    qty = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()

    if pd.isna(qty):
        return None, 'BLANK'

    try:
        qty = float(qty)
    except:
        return None, 'BLANK'

    if unit in ('KGS', 'KG'):
        return qty / 1000, 'DIRECT'
    if unit in ('MTS', 'MT'):
        return qty, 'DIRECT'
    if unit in ('ML', 'LTR'):
        return qty / 1_000_000, 'DIRECT'

    if unit in ('NOS', 'PCS', 'CTN'):
        try:
            clean = desc.replace(" X ", "X").replace("*", "X")

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)G', clean)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)KG', clean)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1000, 'PARSED'

        except:
            return None, 'BLANK'

    return None, 'BLANK'

# ================================================================
# PROCESS FILE
# ================================================================
def process_file(file, excl_df):
    df = pd.read_excel(file)

    hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)

    df[hs_col] = pd.to_numeric(df[hs_col], errors='coerce')
    df = df[df[hs_col].isin(ALL_CODES)].copy()

    primary_mask = df[hs_col].isin(COFFEE_CODES + CHICORY_CODES)
    candidate_mask = df[hs_col].isin(CANDIDATE_CODES)

    primary_df = df[primary_mask].copy()
    candidate_df = df[candidate_mask].copy()

    results = primary_df.apply(
        lambda r: should_exclude(r['PRODUCT DESCRIPTION'], r[hs_col], excl_df), axis=1
    )

    primary_df['_excl'] = [x[0] for x in results]
    primary_df['_reason'] = [x[1] for x in results]

    removed = primary_df[primary_df['_excl']].copy()
    keep = primary_df[~primary_df['_excl']].copy()

    coffee = keep[keep[hs_col].isin(COFFEE_CODES)].copy()
    chicory = keep[keep[hs_col].isin(CHICORY_CODES)].copy()

    if not candidate_df.empty:
        candidate_df['_class'] = candidate_df['PRODUCT DESCRIPTION'].apply(classify_candidate)

        coffee = pd.concat([coffee, candidate_df[candidate_df['_class'] == 'COFFEE']], ignore_index=True)
        chicory = pd.concat([chicory, candidate_df[candidate_df['_class'] == 'CHICORY']], ignore_index=True)
        removed = pd.concat([removed, candidate_df[candidate_df['_class'] == 'EXCLUDE']], ignore_index=True)

    for d in [coffee, chicory]:
        if len(d):
            mt = d.apply(convert_to_mt, axis=1)
            d['MT'] = [x[0] for x in mt]
            d['STATUS'] = [x[1] for x in mt]

    return coffee, chicory, removed

# ================================================================
# UI PIPELINE
# ================================================================
st.markdown('<div class="pipeline">', unsafe_allow_html=True)

excl = st.file_uploader("Exclusion List", type=["xlsx"])
raws = st.file_uploader("Raw Files", type=["xlsx"], accept_multiple_files=True)

if st.button("Run"):
    excl_df = pd.read_excel(excl)

    for f in raws:
        c, ch, e = process_file(f, excl_df)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            c.to_excel(w, sheet_name="Coffee", index=False)
            ch.to_excel(w, sheet_name="Chicory", index=False)
            e.to_excel(w, sheet_name="Excluded", index=False)

        st.download_button(
            label=f"Download {f.name}",
            data=buf.getvalue(),
            file_name=f"CLEANED_{f.name}"
        )
