import streamlit as st
import pandas as pd
import io
import re
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

# ---------------- PAGE CONFIG ----------------

st.set_page_config(page_title="Coffee Trade Intelligence", layout="wide")

# ---------------- HERO ----------------

st.markdown("""
<style>
.stApp {background: #020617; color: white;}
.hero {
    background: linear-gradient(rgba(2,6,23,0.75), rgba(2,6,23,0.95)),
                url("https://images.unsplash.com/photo-1498804103079-a6351b050096");
    padding: 80px 40px; border-radius: 16px; margin-bottom: 40px;
}
.section {background:#f8fafc; padding:40px; border-radius:16px;}
</style>

<div class="hero">
<h1>Coffee Trade Intelligence</h1>
<p>Upload → Clean → Convert → Download</p>
</div>
""", unsafe_allow_html=True)

# ---------------- HSN ----------------

COFFEE_CODES  = [21011110, 21011120, 21011130, 21011190, 21011200]
CHICORY_CODES = [210130, 21013010]
ALL_CODES     = COFFEE_CODES + CHICORY_CODES

STRICT_COFFEE_CHECK_CODES = [21011190, 21011200]

# ---------------- SIGNALS ----------------

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

# ---------------- FILTER ----------------

def should_exclude(desc, hsn, excl_df):
    desc = str(desc).upper()
    hsn = int(hsn) if pd.notna(hsn) else 0

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

# ---------------- MT ----------------

def convert_to_mt(row):
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()

    if pd.isna(qty):
        return None, 'BLANK'

    if unit in ('KGS', 'KG'):
        return qty / 1000, 'DIRECT'

    if unit in ('MTS', 'MT'):
        return qty, 'DIRECT'

    if unit in ('NOS', 'PCS', 'CTN'):
        m = re.search(r'([\d.]+)\s*G', desc)
        if m:
            return qty * float(m.group(1)) / 1_000_000, 'PARSED'

    return None, 'BLANK'

# ---------------- PROCESS ----------------

def process_file(file, excl_df):
    df = pd.read_excel(file)

    hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)

    df = df[df[hs_col].isin(ALL_CODES)]

    keep, removed = [], []

    for _, r in df.iterrows():
        ex, reason = should_exclude(r['PRODUCT DESCRIPTION'], r[hs_col], excl_df)
        if ex:
            r = r.copy()
            r['REASON'] = reason
            removed.append(r)
        else:
            keep.append(r)

    df = pd.DataFrame(keep)

    coffee  = df[df[hs_col].isin(COFFEE_CODES)].copy()
    chicory = df[df[hs_col].isin(CHICORY_CODES)].copy()

    for d in [coffee, chicory]:
        if len(d):
            results = d.apply(convert_to_mt, axis=1)
            d['MT']               = [x[0] for x in results]
            d['MT_CONVERSION_STATUS'] = [x[1] for x in results]

    return coffee, chicory, pd.DataFrame(removed)

# ---------------- UI ----------------

st.subheader("Upload Files")

excl = st.file_uploader("Exclusion List", type=["xlsx"])
raws = st.file_uploader("Raw CYBEX Files", type=["xlsx"], accept_multiple_files=True)

if st.button("Run"):
    if not excl:
        st.error("Please upload an exclusion list.")
    elif not raws:
        st.error("Please upload at least one raw file.")
    else:
        excl_df = pd.read_excel(excl)

        for f in raws:
            c, ch, e = process_file(f, excl_df)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                c.to_excel(w,  sheet_name="Coffee",   index=False)
                ch.to_excel(w, sheet_name="Chicory",  index=False)
                e.to_excel(w,  sheet_name="Excluded", index=False)
            buf.seek(0)

            st.download_button(
                label=f"Download {f.name}",
                data=buf,
                file_name=f"MT_CLEANED_{f.name}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
