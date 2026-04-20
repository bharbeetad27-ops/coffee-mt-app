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
.section {
 background: #f8fafc;
 padding: 40px;
 border-radius: 16px;
 margin-bottom: 40px;
}
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

STRONG_SIGNALS = [
    "INSTANT", "SOLUBLE", "AGGLOMERATED",
    "SPRAY DRIED", "FREEZE DRIED", "EXTRACT"
]

HARD_EXCLUDE = [
    "TEA", "CHAI",
    "CHUKKU", "SUKKU", "MALLI",
    "GINGER", "HERBAL",
    "DOSA", "IDLI", "UPMA",
    "JAMUN", "JALEBI"
]

# ================================================================
# VALIDATION FUNCTION
# ================================================================
def is_valid_soluble(desc):
    desc = str(desc).upper()

    if "COFFEE" not in desc:
        return False

    if not any(x in desc for x in STRONG_SIGNALS):
        return False

    if any(x in desc for x in HARD_EXCLUDE):
        return False

    return True

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
# PROCESS FUNCTION
# ================================================================
def process_file(file):
    df = pd.read_excel(file)

    hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)
    df[hs_col] = pd.to_numeric(df[hs_col], errors='coerce')

    # Clean description
    df["DESC"] = df["PRODUCT DESCRIPTION"].astype(str).str.upper()

    # Flags
    df["IS_HS_COFFEE"] = df[hs_col].isin(COFFEE_CODES)
    df["IS_SOLUBLE"] = df["DESC"].apply(is_valid_soluble)

    # Combine logic
    df["FINAL_INCLUDE"] = df["IS_HS_COFFEE"] | df["IS_SOLUBLE"]

    # Remove junk even inside correct HS
    df.loc[df["IS_HS_COFFEE"], "FINAL_INCLUDE"] = df.apply(
        lambda r: False if any(x in r["DESC"] for x in HARD_EXCLUDE) else True,
        axis=1
    )

    coffee = df[df["FINAL_INCLUDE"]].copy()
    removed = df[~df["FINAL_INCLUDE"]].copy()

    # Misclassified coffee
    wrong_hs = coffee[~coffee[hs_col].isin(COFFEE_CODES)].copy()

    # MT conversion
    if len(coffee):
        mt = coffee.apply(convert_to_mt, axis=1)
        coffee["MT"] = [x[0] for x in mt]
        coffee["STATUS"] = [x[1] for x in mt]

    return coffee, removed, wrong_hs

# ================================================================
# UI PIPELINE (UNCHANGED)
# ================================================================
st.markdown('<div class="pipeline">', unsafe_allow_html=True)

raws = st.file_uploader("Raw Files", type=["xlsx"], accept_multiple_files=True)

if st.button("Run"):
    for f in raws:
        c, e, w = process_file(f)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            c.to_excel(writer, sheet_name="Coffee", index=False)
            e.to_excel(writer, sheet_name="Excluded", index=False)
            w.to_excel(writer, sheet_name="Wrong HS Coffee", index=False)

        st.download_button(
            label=f"Download {f.name}",
            data=buf.getvalue(),
            file_name=f"CLEANED_{f.name}"
        )
