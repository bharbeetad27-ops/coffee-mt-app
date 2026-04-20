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
CHICORY_CODES = [210130, 21013010]
ALL_CODES = COFFEE_CODES + CHICORY_CODES
STRICT_COFFEE_CHECK_CODES = [21011190, 21011200]

COFFEE_SIGNALS = ['COFFEE','KAPPI','CAPPI','NESCAFE','BRU','LEVISTA','DAVIDOFF']
WEAK_COFFEE_SIGNALS = ['PREMIX','MIX','3 IN 1','2 IN 1']
TEA_SIGNALS = ['TEA','CHAI']

# ================================================================
# FIXED EXCLUSION FUNCTION
# ================================================================
def should_exclude(desc, hsn, excl_df):
    desc = str(desc).upper()

    # 1. Exclusion list FIRST
    for _, r in excl_df.iterrows():
        keyword = str(r['KEYWORD']).upper().strip()
        if keyword and keyword in desc:
            return True, r['REASON']

    # 2. Strict coffee logic
    hsn = int(hsn) if pd.notna(hsn) else 0

    if hsn in STRICT_COFFEE_CHECK_CODES:
        strong = any(s in desc for s in COFFEE_SIGNALS)
        weak = any(s in desc for s in WEAK_COFFEE_SIGNALS)
        tea = any(s in desc for s in TEA_SIGNALS)

        if strong:
            return False, ''
        elif tea:
            return True, "Tea detected"
        elif weak:
            return False, "Premix assumed coffee"
        else:
            return True, "No coffee signal"

    return False, ''

# ================================================================
# MT FUNCTION (UNCHANGED)
# ================================================================
def convert_to_mt(row):
    qty = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper()

    if pd.isna(qty):
        return None, 'BLANK'

    try:
        qty = float(qty)
    except:
        return None, 'BLANK'

    if unit in ('KGS','KG'):
        return qty / 1000, 'DIRECT'
    if unit in ('MTS','MT'):
        return qty, 'DIRECT'

    return None, 'BLANK'

# ================================================================
# PROCESS FUNCTION (FIXED)
# ================================================================
def process_file(file, excl_df):
    df = pd.read_excel(file)

    hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)

    # -------- CLEAN DESC --------
    df["DESC"] = df["PRODUCT DESCRIPTION"].astype(str).str.upper()

    # -------- BASE DATA --------
    base_df = df[df[hs_col].isin(ALL_CODES)].copy()

    # -------- MISCLASSIFIED COFFEE --------
    strong_pattern = r"INSTANT|SOLUBLE|AGGLOMERATED|SPRAY DRIED|FREEZE DRIED|EXTRACT"

    df["IS_SOLUBLE"] = (
        df["DESC"].str.contains("COFFEE", na=False) &
        df["DESC"].str.contains(strong_pattern, regex=True, na=False)
    )

    misclassified = df[
        (~df[hs_col].isin(ALL_CODES)) &
        (df["IS_SOLUBLE"])
    ].copy()

    # -------- COMBINE --------
    df = pd.concat([base_df, misclassified], ignore_index=True)

    # -------- EXCLUSION (FASTER) --------
    results = [
        should_exclude(desc, hsn, excl_df)
        for desc, hsn in zip(df["DESC"], df[hs_col])
    ]

    df['_excl'] = [x[0] for x in results]
    df['_reason'] = [x[1] for x in results]

    removed = df[df['_excl']].copy()
    removed['REASON'] = removed['_reason']

    keep = df[~df['_excl']].copy()

    coffee = keep[keep[hs_col].isin(COFFEE_CODES)].copy()
    chicory = keep[keep[hs_col].isin(CHICORY_CODES)].copy()

    for d in [coffee, chicory]:
        if len(d):
            mt_results = d.apply(convert_to_mt, axis=1)
            d['MT'] = [x[0] for x in mt_results]
            d['STATUS'] = [x[1] for x in mt_results]

    return coffee, chicory, removed

# ================================================================
# UI (UNCHANGED)
# ================================================================
st.markdown('<div class="pipeline">', unsafe_allow_html=True)

st.subheader("Stage 1 — Upload Exclusion List")
excl = st.file_uploader("Exclusion List", type=["xlsx"])

st.subheader("Stage 2 — Upload Raw Data")
raws = st.file_uploader("Raw CYBEX Files", type=["xlsx"], accept_multiple_files=True)

if st.button("Run"):
    if not excl:
        st.error("Upload exclusion list")
    elif not raws:
        st.error("Upload files")
    else:
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
