import streamlit as st
import pandas as pd
import io
import re

# ================= CONFIG =================
COFFEE_CODES = [21011110, 21011120, 21011130, 21011190, 21011200]
CHICORY_CODES = [21012010, 21012020, 21012030, 21012090]
VALID_CODES = COFFEE_CODES + CHICORY_CODES

REMOVE_KEYWORDS = [
    'INSTANT TEA','TEA POWDER','TEA EXTRACT','TEA PREMIX',
    'BLACK TEA','GREEN TEA','CHAI','HERBAL TEA','TURMERIC LATTE'
]

KEEP_KEYWORDS = [
    'SOLUBLE COFFEE','INSTANT COFFEE','SPRAY DRIED COFFEE',
    'FREEZE DRIED COFFEE','COFFEE PREMIX','COFFEE EXTRACT',
    'BRU','NESCAFE','DAVIDOFF','LEVISTA','COTHAS'
]

STRONG_COFFEE = [
    "INSTANT","SOLUBLE","AGGLOMERATED",
    "SPRAY DRIED","FREEZE DRIED","EXTRACT"
]

# ================= HELPERS =================
def should_remove(desc):
    desc = str(desc).upper()
    if any(k in desc for k in KEEP_KEYWORDS):
        return False
    return any(k in desc for k in REMOVE_KEYWORDS)

def is_coffee(desc):
    desc = str(desc).upper()
    return "COFFEE" in desc and any(s in desc for s in STRONG_COFFEE)

def get_chicory_fraction(desc):
    desc = str(desc).upper()
    match = re.search(r'(\d+):(\d+)', desc)
    if match:
        c, ch = int(match.group(1)), int(match.group(2))
        if c + ch == 100:
            return ch / 100
    return 0

def convert_to_mt(qty, unit):
    if pd.isna(qty): return None
    unit = str(unit).upper()
    if unit == 'KGS': return qty / 1000
    if unit == 'MTS': return qty
    return None

# ================= CORE =================
def process(df):
    hs_col = next(c for c in df.columns if 'HS' in c.upper())
    desc_col = next(c for c in df.columns if 'DESC' in c.upper())

    df[hs_col] = pd.to_numeric(df[hs_col], errors='coerce')
    df["DESC"] = df[desc_col].astype(str).str.upper()

    # 1. CLEAN DATA
    df_valid = df[df[hs_col].isin(VALID_CODES)].copy()
    df_valid = df_valid[~df_valid["DESC"].apply(should_remove)]

    # 2. HS → PRODUCT ERRORS
    hs_errors = df_valid[
        df_valid["DESC"].apply(lambda x: any(k in x for k in REMOVE_KEYWORDS))
    ]

    # 3. PRODUCT → HS ERRORS
    prod_errors = df[
        (~df[hs_col].isin(VALID_CODES)) &
        (df["DESC"].apply(is_coffee))
    ]

    # 4. METRICS
    if 'STANDARD QUANTITY' in df_valid.columns:
        df_valid["TOTAL_SOLUBLE_MT"] = df_valid.apply(
            lambda r: convert_to_mt(r['STANDARD QUANTITY'], r.get('STANDARD QUANTITY UNIT','')), axis=1
        )

        df_valid["CHICORY_FRACTION"] = df_valid["DESC"].apply(get_chicory_fraction)

        df_valid["PURE_COFFEE_MT"] = df_valid.apply(
            lambda r: r["TOTAL_SOLUBLE_MT"] * (1 - r["CHICORY_FRACTION"])
            if pd.notna(r["TOTAL_SOLUBLE_MT"]) else None,
            axis=1
        )

        df_valid["IMPLIED_CHICORY_MT"] = (
            df_valid["TOTAL_SOLUBLE_MT"] - df_valid["PURE_COFFEE_MT"]
        )

    return df_valid, hs_errors, prod_errors

# ================= UI =================
st.title("Coffee Trade Intelligence")

files = st.file_uploader("Upload files", type=["xlsx"], accept_multiple_files=True)

if st.button("Run"):
    for f in files:
        df = pd.read_excel(f)
        clean, hs_err, prod_err = process(df)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            clean.to_excel(writer, "Clean Data", index=False)
            hs_err.to_excel(writer, "HS Errors", index=False)
            prod_err.to_excel(writer, "Product Errors", index=False)

        st.download_button(
            f"Download {f.name}",
            buffer.getvalue(),
            file_name=f"CLEANED_{f.name}"
        )
