import streamlit as st
import pandas as pd
import numpy as np
import io
import re
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

# ================================================================
# PAGE CONFIG & CSS
# ================================================================
st.set_page_config(page_title="Coffee Trade Intelligence", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #050a0f;
    color: #e2e8f0;
    font-family: 'Syne', sans-serif;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }

/* ── HERO ── */
.hero {
    position: relative;
    overflow: hidden;
    padding: 60px 48px 52px;
    margin-bottom: 48px;
    border-radius: 2px;
    background: #050a0f;
    border-left: 3px solid #00d4aa;
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(0,212,170,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.22em;
    color: #00d4aa;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero h1 {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.05;
    margin: 0 0 16px 0;
    color: #f8fafc;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    color: #64748b;
    letter-spacing: 0.04em;
}

/* ── STAGE HEADERS ── */
.stage-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 36px 0 18px 0;
}
.stage-num {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    color: #00d4aa;
    border: 1px solid #00d4aa22;
    padding: 4px 10px;
    border-radius: 2px;
    background: #00d4aa08;
}
.stage-title {
    font-size: 18px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.01em;
}

/* ── TIER CARDS ── */
.tier-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin: 24px 0;
}
.tier-card {
    background: #0d1520;
    border: 1px solid #1e2d3d;
    border-radius: 2px;
    padding: 20px 16px;
    position: relative;
    overflow: hidden;
}
.tier-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.tier-card.observed::before  { background: #00d4aa; }
.tier-card.tier1::before     { background: #3b82f6; }
.tier-card.tier1b::before    { background: #8b5cf6; }
.tier-card.tier1c::before    { background: #a78bfa; }
.tier-card.tier2::before     { background: #f59e0b; }
.tier-card.tier3::before     { background: #ef4444; }
.tier-card.irrecov::before   { background: #374151; }

.tier-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 8px;
}
.tier-count {
    font-size: 32px;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1;
    font-family: 'Syne', sans-serif;
}
.tier-pct {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #475569;
    margin-top: 4px;
}

/* ── PROGRESS BAR ── */
.tier-bar-wrap {
    height: 6px;
    background: #0d1520;
    border-radius: 1px;
    overflow: hidden;
    display: flex;
    margin: 20px 0 24px;
}
.tier-bar-seg { height: 100%; }

/* ── RESULT BOX ── */
.result-box {
    background: #0a1525;
    border: 1px solid #1e2d3d;
    border-radius: 2px;
    padding: 24px 28px;
    margin: 16px 0;
}
.result-box-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    color: #00d4aa;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.result-mt {
    font-size: 28px;
    font-weight: 800;
    color: #f8fafc;
}
.result-mt-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #475569;
    margin-top: 4px;
}

/* ── STREAMLIT OVERRIDES ── */
.stButton > button {
    background: #00d4aa !important;
    color: #050a0f !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.04em !important;
    padding: 10px 32px !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stDownloadButton > button {
    background: transparent !important;
    color: #00d4aa !important;
    border: 1px solid #00d4aa44 !important;
    border-radius: 2px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.06em !important;
    transition: border-color 0.15s !important;
}
.stDownloadButton > button:hover { border-color: #00d4aa !important; }

div[data-testid="stFileUploader"] {
    background: #0d1520 !important;
    border: 1px dashed #1e2d3d !important;
    border-radius: 2px !important;
    padding: 8px !important;
}

.stDataFrame { border-radius: 2px !important; }

.stSpinner > div { color: #00d4aa !important; }

[data-testid="stSuccess"] {
    background: #00d4aa0d !important;
    border: 1px solid #00d4aa33 !important;
    border-radius: 2px !important;
    color: #00d4aa !important;
}
[data-testid="stError"] {
    background: #ef44440d !important;
    border: 1px solid #ef444433 !important;
    border-radius: 2px !important;
}

.stSelectbox > div > div {
    background: #0d1520 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 2px !important;
}

h2, h3 { font-family: 'Syne', sans-serif !important; }

.divider {
    border: none;
    border-top: 1px solid #1e2d3d;
    margin: 40px 0;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# CONSTANTS — HSN BUCKETS
# ================================================================
SOLUBLE_COFFEE_HSN = {21011110, 21011120, 21011130, 21011190}
CHICORY_PREMIX_HSN = {21011200}
ALL_TARGET_HSN     = SOLUBLE_COFFEE_HSN | CHICORY_PREMIX_HSN
CHICORY_ONLY_HSN   = {21013010}
PURE_CHICORY_HSN   = {21013090, 21012020}
GROUND_COFFEE_HSN  = {9012190, 9019090, 9019020, 9011119, 9011129, 9012290}

SOLUBLE_KEYWORDS = [
    'INSTANT COFFEE', 'SOLUBLE COFFEE', 'SPRAY DRIED COFFEE', 'FREEZE DRIED COFFEE',
    'AGGLOMERATED COFFEE', 'AGGLOMERATED INSTANT', 'FREEZE-DRIED COFFEE',
    'SPRAY-DRIED COFFEE', 'COFFEE EXTRACT POWDER', 'COFFEE PREMIX',
    'NESCAFE', 'BRU INSTANT', 'SUNRISE EXTRA',
]
CHICORY_WRONG_HSN_KEYWORDS = ['CHICORY', 'CHICCORY']

sol_pattern    = '|'.join(re.escape(k) for k in SOLUBLE_KEYWORDS)
chic_wrong_pat = '|'.join(re.escape(k) for k in CHICORY_WRONG_HSN_KEYWORDS)

_ADMIN_PATTERNS = re.compile(
    r'\b(?:GSTIN(?=\W)|GSTN(?=\W)|GST\s+NO(?=\W)'
    r'|TAX\s+INV(?:OICE)?|INV\s*NO|INVOICE\s*NO'
    r'|ICO\s+SI\s+NUMBER|ICO\s+MARK\s+NO|PERMIT\s+NUMBER'
    r'|REF\s*NO\.?:)', re.IGNORECASE,
)
_MERCH_PATTERNS = re.compile(
    r'\b(?:TSHIRT|T-SHIRT|SAMPLING\s+TABLE|PROMOTIONAL\s+MATERIAL)', re.IGNORECASE,
)
_strict_coffee_signal_pattern = re.compile(
    r'COFFEE|CAPPUCCINO|CAPUCCINO|NESCAFE|BRU|LEVISTA|COTHAS|CONTINENTAL|NARASUS|TATA COFFEE|CHICORY|PREMIX',
    re.IGNORECASE
)
STRICT_CHECK_HSNS = {'21011190', '21011200'}

QUANTITY_AWARE_EXCLUSIONS = [
    ('FREE SAMPLE',          0.05, 'FOC sample — below 50 KGS commercial threshold'),
    ('SAMPLE',               0.05, 'Sample shipment — below 50 KGS commercial threshold'),
    ('TEST REPORT',          0.02, 'QC/test sample — below 20 KGS'),
    ('FOR EXHIBITION',       0.10, 'Exhibition goods — NCV below 100 KGS'),
    ('EXHIBITION GOODS',     0.10, 'Exhibition goods — NCV below 100 KGS'),
    ('NO COMMERCIAL VALUE',  0.10, 'Explicitly NCV — below 100 KGS'),
    ('NCV',                  0.10, 'Explicitly NCV — no commercial value'),
    ('NOT FOR SALE',         0.05, 'Not-for-sale — below 50 KGS'),
    ('FREE OF COST',         0.05, 'FOC shipment — below 50 KGS'),
    ('PROMOTIONAL MATERIAL', 0.05, 'Promotional material — below 50 KGS'),
    ('GIFT',                 0.02, 'Gift/personal shipment — below 20 KGS'),
    ('PERSONAL USE',         0.02, 'Personal use — not commercial trade'),
]


# ================================================================
# IMPUTATION CONSTANTS
# ================================================================
PACKAGING_BENCHMARKS = {
    "BAG":       (0.060, 0.050, 0.060),
    "SACK":      (0.060, 0.050, 0.060),
    "FIBC":      (1.000, 0.900, 1.100),
    "BIG BAG":   (1.000, 0.900, 1.100),
    "JUMBO":     (0.500, 0.400, 0.600),
    "SUPER":     (0.500, 0.400, 0.600),
    "TEU":       (21.00, 19.00, 24.00),
    "20FT":      (21.00, 19.00, 24.00),
    "40FT":      (26.40, 26.40, 27.50),
    "FTE":       (26.40, 26.40, 27.50),
    "CONTAINER": (21.00, 19.00, 24.00),
}
WEIGHT_UNIT_MAP = {
    "KGS": 0.001, "KG": 0.001, "GMS": 0.000001, "GRM": 0.000001,
    "G": 0.000001, "LBS": 0.000454, "MT": 1.0, "MTS": 1.0, "TON": 1.0, "TONS": 1.0,
}

ICO_PRICES = {
    "SOLUBLE": 9500, "ROASTED": 6500, "GREEN": 4700, "DEFAULT": 5000,
}

IMP_CFG = {
    "suv_min_obs_high":        10,
    "suv_min_obs_low":         5,
    "outlier_ratio_threshold": 100,
    "outlier_floor_mt":        0.1,
    "max_plausible_mt":        30 * 28.28,
    "min_plausible_mt":        0.000001,
}

_UNIT_TO_G = {"KG": 1000.0, "KGS": 1000.0, "GM": 1.0, "GMS": 1.0, "G": 1.0}

_BULK_PATTERNS_T1B = [
    re.compile(r'(?<![0-9A-Z])[Xx]\s*(25|20|22|23|30)\s*KGS?\b(?!\s*/)', re.IGNORECASE),
    re.compile(r'\bEACH\s+CARTON\s+CONSIST\s+OF\s+(25|20|22|23|30)\s*KGS?\b', re.IGNORECASE),
    re.compile(r'\bPER\s+CARTON[^)]{0,30}(25|20|22|23|30)\s*KGS?\b', re.IGNORECASE),
    re.compile(r'\b(25|20|22|23|30)\s*KGS?\s+(?:NET\s+)?(?:EACH|PER)\b', re.IGNORECASE),
    re.compile(r'\bBULK\b', re.IGNORECASE),
]
_P3       = re.compile(r'(\d+(?:\.\d+)?)\s*(KGS?|KG)\s*NET\b', re.IGNORECASE)
_P1_MULTI = re.compile(r'(\d+)\s*[Xx]\s*(\d+(?:\.\d+)?)\s*(KGS?|KG|GMS?|GM|G)\s*[Xx]\s*(\d+)\s*(?:BOTTLES?|JARS?|CANS?|TINS?|PACKS?|PCS?|NOS?|UNITS?)?', re.IGNORECASE)
_P1       = re.compile(r'(\d+)\s*[Xx]\s*(\d+(?:\.\d+)?)\s*(KGS?|KG|GMS?|GM|G)\b', re.IGNORECASE)
_P2       = re.compile(r'(\d+(?:\.\d+)?)\s*(GMS?|GM|G|KGS?|KG)\s*[Xx]\s*(\d+)\s*(?:NOS?|PCS?|UNITS?|STICKS?|SACHETS?)?', re.IGNORECASE)
_P4       = re.compile(r'\(\s*(\d+(?:\.\d+)?)\s*(GMS?|GM|G)\s*[Xx]\s*(\d+)\s*(?:PCS?|NOS?|TINS?|JARS?|CANS?|UNITS?)?\s*\)', re.IGNORECASE)

_BRAND_KEYWORDS = [
    "NESCAFE", "BOSCAFE", "SUNRISE", "DAVIDOFF", "NESCAFÉ", "BRU", "CONTINENTAL",
    "TATA COFFEE", "TATA", "MOCCONA", "DOUWE EGBERTS", "FOLGERS", "MAXWELL",
    "TCHIBO", "JACOBS", "LAVAZZA", "ILLY", "KOPIKO", "CAFE DESIRE", "CAFE VENDING",
    "AGGLOMERATED", "FREEZE DRIED", "SPRAY DRIED",
]
_STOP_WORDS_PEER = {
    "COFFEE", "INSTANT", "SOLUBLE", "ROASTED", "GROUND", "EXPORT", "INDIA",
    "NOS", "PCS", "UNITS", "CARTONS", "KGS", "KG", "GMS", "GM", "NET", "GROSS",
}


# ================================================================
# STAGE 1 — EXCLUSION LIST
# ================================================================
@st.cache_data
def build_excl_list_lookup(excl_df_json):
    excl_df = pd.read_json(io.StringIO(excl_df_json))
    global_kws, hsn_kws = {}, {}
    has_kw  = 'KEYWORD'    in excl_df.columns
    has_hsn = 'HSN_FILTER' in excl_df.columns
    has_rsn = 'REASON'     in excl_df.columns
    kw_col  = excl_df['KEYWORD'].astype(str).str.upper().str.strip()    if has_kw  else pd.Series([''] * len(excl_df))
    hsn_col = excl_df['HSN_FILTER'].astype(str).str.strip()             if has_hsn else pd.Series([''] * len(excl_df))
    rsn_col = excl_df['REASON'].astype(str)                             if has_rsn else pd.Series(['Exclusion list match'] * len(excl_df))
    valid     = kw_col != ''
    is_global = valid & hsn_col.isin(['', 'nan', 'NAN'])
    is_hsn    = valid & ~hsn_col.isin(['', 'nan', 'NAN'])
    for kw, rsn in zip(kw_col[is_global], rsn_col[is_global]):
        global_kws[kw] = rsn
    for kw, hsn, rsn in zip(kw_col[is_hsn], hsn_col[is_hsn], rsn_col[is_hsn]):
        hsn_kws.setdefault(hsn, {})[kw] = rsn
    return global_kws, hsn_kws


def apply_exclusions_vectorised(df, excl_global_kws, excl_hsn_kws):
    desc  = df['_DESC_UP']
    hsn_s = df['_HSN_INT'].astype(str)
    qty_col  = next((c for c in ['STANDARD QUANTITY', 'QUANTITY', 'QTY', 'STD QTY'] if c in df.columns), None)
    unit_col = next((c for c in ['UNIT', 'STANDARD QUANTITY UNIT', 'UOM', 'QTY UNIT'] if c in df.columns), None)
    if qty_col:
        raw_qty = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
        if unit_col:
            unit_s = df[unit_col].astype(str).str.strip().str.upper()
            qty_mt = pd.Series(float('nan'), index=df.index)
            qty_mt = qty_mt.where(~unit_s.isin(['KGS', 'KG']), raw_qty / 1000)
            qty_mt = qty_mt.where(~unit_s.isin(['MTS', 'MT']), raw_qty)
        else:
            qty_mt = raw_qty / 1000
    else:
        qty_mt = pd.Series(float('nan'), index=df.index)

    n        = len(df)
    excluded = np.zeros(n, dtype=bool)
    reason   = np.full(n, '', dtype=object)

    hit = desc.str.contains(_ADMIN_PATTERNS, na=False)
    excluded |= hit.values
    reason[hit.values & (reason == '')] = 'Administrative/reference row'

    not_yet = ~pd.Series(excluded, index=df.index)
    merch_hit = not_yet & desc.str.contains(_MERCH_PATTERNS, na=False)
    pos = df.index.get_indexer(merch_hit[merch_hit].index)
    excluded[pos] = True
    for p in pos:
        if reason[p] == '': reason[p] = 'Merchandise giveaway'

    not_yet = ~pd.Series(excluded, index=df.index)
    mug_hit = not_yet & desc.str.contains(r'\bMUG\b', na=False)
    no_cs   = ~desc.str.contains(_strict_coffee_signal_pattern, na=False)
    mug_j   = mug_hit & no_cs
    pos = df.index.get_indexer(mug_j[mug_j].index)
    excluded[pos] = True
    for p in pos:
        if reason[p] == '': reason[p] = 'Merchandise giveaway — standalone mug'

    if excl_global_kws:
        user_global_pat = re.compile('|'.join(re.escape(k) for k in excl_global_kws), re.IGNORECASE)
        mask = ~pd.Series(excluded, index=df.index)
        if mask.any():
            hit = desc[mask].str.contains(user_global_pat, na=False)
            for idx in hit[hit].index:
                loc = df.index.get_loc(idx)
                if not excluded[loc]:
                    d = desc.at[idx]
                    for kw, rsn in excl_global_kws.items():
                        if kw in d:
                            reason[loc] = rsn; break
                    excluded[loc] = True

    for hsn_str, kw_dict in excl_hsn_kws.items():
        hsn_mask = (hsn_s == hsn_str) & (~pd.Series(excluded, index=df.index))
        if not hsn_mask.any(): continue
        for kw, rsn in kw_dict.items():
            hit = desc[hsn_mask].str.contains(re.escape(kw), na=False, regex=True)
            idx = hit[hit].index
            pos = df.index.get_indexer(idx)
            excluded[pos] = True
            for p in pos:
                if reason[p] == '': reason[p] = rsn

    strict_mask = hsn_s.isin(STRICT_CHECK_HSNS) & (~pd.Series(excluded, index=df.index))
    if strict_mask.any():
        has_signal = desc[strict_mask].str.contains(_strict_coffee_signal_pattern, na=False)
        no_signal  = strict_mask & (~has_signal.reindex(df.index, fill_value=False))
        pos = df.index.get_indexer(no_signal[no_signal].index)
        excluded[pos] = True
        for p in pos:
            if reason[p] == '': reason[p] = 'No coffee signal — strict HSN check'

    not_yet_excluded = ~pd.Series(excluded, index=df.index)
    for kw, qty_threshold, junk_reason in QUANTITY_AWARE_EXCLUSIONS:
        if not not_yet_excluded.any(): break
        kw_hit   = not_yet_excluded & desc.str.contains(re.escape(kw), na=False)
        low_qty  = qty_mt < qty_threshold
        junk_hit = kw_hit & low_qty
        pos = df.index.get_indexer(junk_hit[junk_hit].index)
        excluded[pos] = True
        for p in pos:
            if reason[p] == '': reason[p] = junk_reason
        not_yet_excluded = not_yet_excluded & ~junk_hit

    return pd.Series(excluded, index=df.index), pd.Series(reason, index=df.index)


# ================================================================
# STAGE 1 — HSN BUCKETING
# ================================================================
def norm_hsn_series(series):
    return (series.astype(str).str.replace(r'\s+', '', regex=True)
            .str.split('.').str[0]
            .pipe(pd.to_numeric, errors='coerce').fillna(0).astype(int))

def bucket_hsn_series(hsn_series):
    conditions = [
        hsn_series.isin(SOLUBLE_COFFEE_HSN), hsn_series.isin(CHICORY_PREMIX_HSN),
        hsn_series.isin(CHICORY_ONLY_HSN),   hsn_series.isin(PURE_CHICORY_HSN),
        hsn_series.isin(GROUND_COFFEE_HSN),
    ]
    choices = ['SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY', 'PURE_CHICORY', 'GROUND_COFFEE']
    return pd.Series(np.select(conditions, choices, default='OTHER'), index=hsn_series.index)

def find_wrong_hsn_rows(df, hs_col):
    scannable = ~df['_BUCKET'].isin(['SOLUBLE_COFFEE','CHICORY_PREMIX','CHICORY_ONLY','PURE_CHICORY'])
    df_scan = df[scannable].copy()
    df_scan['_WRONG_SOLUBLE'] = df_scan['_DESC_UP'].str.contains(sol_pattern, na=False, regex=True)
    df_scan['_WRONG_CHICORY'] = df_scan['_DESC_UP'].str.contains(chic_wrong_pat, na=False, regex=True)
    df_scan['_WRONG_ANY']     = df_scan['_WRONG_SOLUBLE'] | df_scan['_WRONG_CHICORY']
    return df_scan[df_scan['_WRONG_ANY']].copy()


# ================================================================
# STAGE 1 — CHICORY CLASSIFICATION
# ================================================================
KNOWN_BRANDS = [
    (r'NESCAFE.*SUNRISE|SUNRISE.*REGULAR|SUNRISE EXTRA|SUNRISE BLENDED|SUNRISE INSTA', 70, 30, 'CONFIRMED', 'Nestle Professional listing'),
    (r'NESCAFE CLASSIC',   100, 0,  'CONFIRMED', 'Pure instant coffee'),
    (r'NESCAFE GOLD',      100, 0,  'CONFIRMED', 'Premium pure coffee'),
    (r'NESCAFE INTENSO',   100, 0,  'CONFIRMED', 'Pure instant — confirmed'),
    (r'NESCAFE',           100, 0,  'ASSUMED',   'Generic Nescafe — assumed pure'),
    (r'BRU.*GOLD|BRU GOLD',100, 0,  'CONFIRMED', 'Pure freeze dried'),
    (r'BRU.*GREEN LABEL|GREEN LABEL.*COFFEE', 80, 20, 'ASSUMED', 'Filter blend'),
    (r'BRU.*SELECT',       85, 15,  'ASSUMED',   'Premium blend'),
    (r'BRU INSTANT|BRU.*OPTIMA|BRU.*OPTM|BRU.*SUPER STRONG|BRU STRONG|BRU.*PLATINA|BRU.*EXPORT|BRU.*STAND UP|BRU.*AROMA|BRU.*INST', 70, 30, 'ASSUMED', 'Known chicory blend'),
    (r'TATA.*GRAND|TATA COFFEE GRAND', 70, 30, 'ASSUMED', 'Chicory mix indicated'),
    (r'TATA.*GOLD|TATA COFFEE GOLD',  100, 0,  'CONFIRMED', 'Pure coffee'),
    (r'TATA.*CLASSIC',     100, 0,  'ASSUMED',   'Usually pure'),
    (r'CONTINENTAL.*MALGUDI', 53, 47,'CONFIRMED', 'Label states 53:47'),
    (r'CONTINENTAL.*XTRA|CONTINENTAL.*STRONG', 70, 30, 'ASSUMED', 'Tradeindia listing'),
    (r'CONTINENTAL.*SPECIAL|CONTINENTAL.*PURE', 100, 0,'CONFIRMED', 'Pure variant'),
    (r'LEVISTA.*CLASSIC',  80, 20,  'ASSUMED',   'Chicory variant'),
    (r'LEVISTA.*80',       80, 20,  'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*70',       70, 30,  'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*60',       60, 40,  'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*PREMIUM|LEVISTA.*PURE', 100, 0, 'ASSUMED', 'Pure line'),
    (r'NARASUS.*UDHAYAM|NARASUS.*UDHAIYAM', 80, 20, 'ASSUMED', 'Blend positioning'),
    (r'NARASUS.*DELITE',   55, 45,  'ASSUMED',   'Label: 55:45'),
    (r'NARASUS.*BESH SUKKU|BESH SUKKU', 70, 30,'ASSUMED', 'Sukku blend'),
    (r'NARASUS.*PURE|NARASUS PURE INSTANT|NARASUS INSTA STRONG|NARASUS STRONG INSTANT|NARASUS INSTANT', 100, 0, 'ASSUMED', 'Pure/instant line'),
    (r'SUNRISE COFFEE|SUNRISE.*BLENDED', 70, 30,'CONFIRMED', 'Nestle Professional listing'),
    (r'COTHAS.*SPECIAL',   80, 20,  'ASSUMED',   'Special filter blend'),
    (r'COTHAS.*PREMIUM',   85, 15,  'ASSUMED',   'Premium blend'),
    (r'COTHAS.*80',        80, 20,  'ASSUMED',   'Ratio in name'),
    (r'KDC.*60|KDC.*70|KDC.*80', None, None, 'EXPLICIT_RATIO', 'Ratio in product name'),
]

def extract_ratio(desc_up):
    m = re.search(r'\b(\d{2})\s*[:/]\s*(\d{2})\b', desc_up)
    if m: return int(m.group(1)), int(m.group(2))
    return None, None

def classify_chicory_row(desc_up):
    has_chicory_word = bool(re.search(r'CHICORY|CHICCORY|CICCORY|RICORY', desc_up))
    ratio_a, ratio_b = extract_ratio(desc_up)
    if has_chicory_word and ratio_a is not None:
        return ('EXPLICIT', ratio_a, ratio_b, 'HIGH', 'Chicory + ratio both stated')
    if has_chicory_word:
        return ('EXPLICIT', None, None, 'MEDIUM', 'Chicory stated, ratio not given')
    if ratio_a is not None:
        return ('EXPLICIT', ratio_a, ratio_b, 'MEDIUM', 'Ratio in description, chicory not named')
    for pattern, c_pct, ch_pct, conf, notes in KNOWN_BRANDS:
        if re.search(pattern, desc_up):
            if conf == 'EXPLICIT_RATIO':
                r_a, r_b = extract_ratio(desc_up)
                if r_a: return ('EXPLICIT', r_a, r_b, 'HIGH', notes)
            if ch_pct == 0: return ('PURE_COFFEE', c_pct, ch_pct, conf, notes)
            return ('KNOWN_BRAND', c_pct, ch_pct, conf, notes)
    return None

CHICORY_SIGNAL_PATTERN = (
    r'CHICORY|CHICCORY|CICCORY|RICORY|'
    r'\b\d{2}\s*[:/]\s*\d{2}\b|'
    r'SUNRISE EXTRA|SUNRISE.*BLENDED|SUNRISE.*INSTA|'
    r'BRU INSTANT|BRU.*OPTIMA|BRU.*OPTM|BRU.*SUPER STRONG|BRU STRONG|BRU.*PLATINA|BRU.*AROMA|'
    r'BRU.*INST(?!.*GOLD)|'
    r'TATA.*GRAND|CONTINENTAL.*MALGUDI|CONTINENTAL.*XTRA|CONTINENTAL.*STRONG|'
    r'NARASUS.*UDHAYAM|NARASUS.*DELITE|NARASUS.*BESH SUKKU|'
    r'LEVISTA.*CLASSIC|LEVISTA.*[678]0'
)


# ================================================================
# STAGE 1 — MT CONVERSION
# ================================================================
STOP_WORDS_MT = ['OF','WITH','AND','FOR','NET','GROSS','EACH','PER','PACK','PKT',
                 'POUCH','BAG','BOX','CASE','CARTON','SACHET','JAR','TIN','CAN',
                 'BOTTLE','UNIT','ASSORTED']
_STOP_PAT = re.compile(r'\b(' + '|'.join(re.escape(w) for w in STOP_WORDS_MT) + r')\b')
PARSE_UNITS = {'NOS', 'PCS', 'CTM', 'CTN'}
DIRECT_KG   = {'KGS', 'KG'}
DIRECT_MT   = {'MTS', 'MT'}
DIRECT_ML   = {'ML', 'MLT', 'LTR'}

def convert_to_mt(row):
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper().strip()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()
    if pd.isna(qty): return np.nan, 'BLANK'
    try: qty = float(qty)
    except: return np.nan, 'BLANK'
    if unit in DIRECT_KG: return qty / 1000, 'DIRECT'
    if unit in DIRECT_MT: return qty, 'DIRECT'
    if unit in DIRECT_ML: return qty / 1_000_000, 'DIRECT'
    if unit in PARSE_UNITS:
        try:
            clean = _STOP_PAT.sub(' ', desc).strip()
            clean = re.sub(r'\s+', ' ', clean)
            clean = clean.replace(' X ', 'X').replace(' x ', 'X').replace('*', 'X')
            patterns_kg = [
                (r'(\d+(?:\.\d+)?)\s*KGS?\s*X\s*(\d+)', lambda m: float(m.group(1)) * float(m.group(2))),
                (r'(\d+(?:\.\d+)?)KGX(\d+)', lambda m: float(m.group(1)) * float(m.group(2))),
                (r'(\d+)X(\d+(?:\.\d+)?)KG\b', lambda m: float(m.group(1)) * float(m.group(2))),
                (r'(\d+(?:\.\d+)?)\s*KGS?\s*NET', lambda m: float(m.group(1))),
            ]
            for pat, fn in patterns_kg:
                m = re.search(pat, clean, re.IGNORECASE)
                if m: return qty * fn(m), 'PARSED'
            patterns_g = [
                (r'(\d+(?:\.\d+)?)\s*GMS?\s*X\s*(\d+)\s*X\s*(\d+)', lambda m: float(m.group(1))*float(m.group(2))*float(m.group(3))/1e6),
                (r'(\d+(?:\.\d+)?)\s*G\s*X\s*(\d+)\s*X\s*(\d+)', lambda m: float(m.group(1))*float(m.group(2))*float(m.group(3))/1e6),
                (r'(\d+)\((\d+)X(\d+(?:\.\d+)?)G\)', lambda m: float(m.group(1))*float(m.group(2))*float(m.group(3))/1e6),
                (r'\((\d+(?:\.\d+)?)\s*GMS?X(\d+)\)', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'\((\d+)X(\d+(?:\.\d+)?)\s*GMS?\)', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+(?:\.\d+)?)\s*GMS\s*X\s*(\d+)', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+(?:\.\d+)?)\s*GMX(\d+)', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+(?:\.\d+)?)\s*GX(\d+)', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+)X(\d+(?:\.\d+)?)\s*GMS\b', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+)X(\d+(?:\.\d+)?)\s*GM\b', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+)X(\d+(?:\.\d+)?)\s*G\b', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+(?:\.\d+)?)\s*MLX(\d+)', lambda m: float(m.group(1))*float(m.group(2))/1e6),
                (r'(\d+)X(\d+(?:\.\d+)?)\s*ML\b', lambda m: float(m.group(1))*float(m.group(2))/1e6),
            ]
            for pat, fn in patterns_g:
                m = re.search(pat, clean, re.IGNORECASE)
                if m: return qty * fn(m), 'PARSED'
            for pat, div in [
                (r'(\d+(?:\.\d+)?)\s*GRAMS?\b', 1e6),
                (r'(\d+(?:\.\d+)?)\s*GRM\b', 1e6),
            ]:
                m = re.search(pat, clean, re.IGNORECASE)
                if m: return qty * float(m.group(1)) / div, 'PARSED'
            for suffix, div in [('GMS', 1e6), ('GM', 1e6), ('G', 1e6), ('KG', 1), ('ML', 1e6)]:
                vals = re.findall(r'(\d+(?:\.\d+)?)\s*' + suffix + r'\b', clean, re.IGNORECASE)
                if vals:
                    val = float(vals[-1])
                    if suffix == 'G' and val >= 5000: continue
                    factor = val / div if suffix != 'KG' else val
                    return qty * factor, 'PARSED'
        except: return np.nan, 'BLANK'
    return np.nan, 'BLANK'

def convert_to_mt_vectorised(df):
    qty  = pd.to_numeric(df.get('STANDARD QUANTITY', pd.Series(dtype=float)), errors='coerce')
    unit = df.get('STANDARD QUANTITY UNIT', pd.Series(dtype=str)).astype(str).str.upper().str.strip()
    is_blank = qty.isna()
    is_kgs   = unit.isin(DIRECT_KG)  & ~is_blank
    is_mt    = unit.isin(DIRECT_MT)  & ~is_blank
    is_ml    = unit.isin(DIRECT_ML)  & ~is_blank
    is_parse = unit.isin(PARSE_UNITS) & ~is_blank
    mt_vals = pd.Series(np.nan, index=df.index)
    status  = pd.Series('BLANK', index=df.index)
    mt_vals[is_kgs] = qty[is_kgs] / 1000;  status[is_kgs] = 'DIRECT'
    mt_vals[is_mt]  = qty[is_mt];          status[is_mt]  = 'DIRECT'
    mt_vals[is_ml]  = qty[is_ml] / 1e6;   status[is_ml]  = 'DIRECT'
    if is_parse.any():
        parsed_results = df[is_parse].apply(convert_to_mt, axis=1)
        mt_vals[is_parse] = parsed_results.apply(lambda x: x[0]).astype(float).values
        status[is_parse]  = parsed_results.apply(lambda x: x[1]).values
    return mt_vals, status


# ================================================================
# STAGE 1 — EXCEL OUTPUT
# ================================================================
EXCEL_SHEETS = [
    '1 All Soluble Coffee', '2 Chicory Explicit Ratio', '3 Chicory Known Brand',
    '4 Chicory Assumed', '5 Chicory Only Exports', 'Summary',
]
SHEET_COLOURS = {
    '1 All Soluble Coffee':      ('1F4E79', 'D6E4F0', 'EBF4FA'),
    '2 Chicory Explicit Ratio':  ('1A5E20', 'D4EDDA', 'EAF7EC'),
    '3 Chicory Known Brand':     ('7B4F00', 'FFF3CD', 'FFFAED'),
    '4 Chicory Assumed':         ('6A0572', 'F3D6F5', 'FAF0FB'),
    '5 Chicory Only Exports':    ('2C3E50', 'D5DBDB', 'F2F3F4'),
    'Summary':                   ('0D3B66', 'D6E4F0', 'EBF4FA'),
}

def _hex(h): return f'#{h}'

def write_excel(sheets_dict):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        for sheet_name in EXCEL_SHEETS:
            if sheet_name not in sheets_dict: continue
            df_out = sheets_dict[sheet_name]
            df_out.to_excel(writer, sheet_name=sheet_name, index=False)
            wb  = writer.book
            ws  = writer.sheets[sheet_name]
            colours = SHEET_COLOURS.get(sheet_name, ('1F4E79', 'D6E4F0', 'EBF4FA'))
            hdr_hex, row1_hex, row2_hex = colours
            hdr_fmt = wb.add_format({'bold': True, 'bg_color': _hex(hdr_hex), 'font_color': '#FFFFFF',
                                     'border': 1, 'border_color': '#CCCCCC', 'align': 'center',
                                     'valign': 'vcenter', 'text_wrap': True, 'font_size': 10})
            row1_fmt = wb.add_format({'bg_color': _hex(row1_hex), 'font_color': '#1A1A1A',
                                      'border': 1, 'border_color': '#CCCCCC', 'font_size': 9})
            row2_fmt = wb.add_format({'bg_color': _hex(row2_hex), 'font_color': '#1A1A1A',
                                      'border': 1, 'border_color': '#CCCCCC', 'font_size': 9})
            for col_idx, col_name in enumerate(df_out.columns):
                ws.write(0, col_idx, col_name, hdr_fmt)
            for row_idx in range(1, len(df_out) + 1):
                ws.set_row(row_idx, None, row1_fmt if row_idx % 2 == 1 else row2_fmt)
            for col_idx, col_name in enumerate(df_out.columns):
                ws.set_column(col_idx, col_idx, min(max(len(str(col_name)) + 4, 10), 40))
            ws.freeze_panes(1, 0)
    buf.seek(0)
    return buf.getvalue()


# ================================================================
# STAGE 2 — IMPUTATION UTILITIES
# ================================================================
def get_hs_prefix(hs_val, length):
    if pd.isna(hs_val): return ""
    s = str(hs_val).strip().replace(".", "")
    return s[:length] if len(s) >= length else s

def detect_hs_ico_group(hs_val):
    hs4 = get_hs_prefix(hs_val, 4); hs5 = get_hs_prefix(hs_val, 5)
    if hs4 == "2101":  return "SOLUBLE"
    if hs5 == "09012": return "ROASTED"
    if hs4 == "0901":  return "GREEN"
    return "DEFAULT"

def parse_unit_canonical(unit_str):
    if pd.isna(unit_str): return "UNKNOWN"
    u = str(unit_str).strip().upper()
    if u in WEIGHT_UNIT_MAP: return u
    for key in PACKAGING_BENCHMARKS:
        if key in u: return key
    return u

def bag_weight_from_unit_price(unit_price_usd):
    if pd.isna(unit_price_usd) or unit_price_usd <= 0: return 60.0
    usd_per_kg = unit_price_usd / 60.0
    if 2.5 <= usd_per_kg <= 10.0: return 60.0
    for bag_kg in [50, 25, 10, 5, 1]:
        if 2.0 <= unit_price_usd / bag_kg <= 15.0: return float(bag_kg)
    return 60.0

def _to_g(value, unit_str):
    key = unit_str.upper().rstrip("S")
    return value * _UNIT_TO_G.get(key, _UNIT_TO_G.get(unit_str.upper(), 1.0))

def extract_carton_weight_kg(description):
    if description is None or (isinstance(description, float) and np.isnan(description)):
        return None, None, None
    d = str(description).upper().strip()
    if not d: return None, None, None
    if any(p.search(d) for p in _BULK_PATTERNS_T1B): return None, None, None
    _MIN, _MAX = 0.001, 50.0
    p3 = _P3.findall(d)
    if p3:
        val, unit = p3[-1]; kg = _to_g(float(val), unit) / 1000.0
        if _MIN <= kg <= _MAX: return kg, "P3_NET_WT", "HIGH"
    p1m = _P1_MULTI.findall(d)
    if p1m:
        n1, w, unit, n2 = p1m[-1]; kg = float(n1)*_to_g(float(w), unit)*float(n2)/1000.0
        if _MIN <= kg <= _MAX: return kg, "P1_MULTI", "HIGH"
    p1 = _P1.findall(d)
    if p1:
        n, w, unit = p1[-1]; kg = float(n)*_to_g(float(w), unit)/1000.0
        if _MIN <= kg <= _MAX: return kg, "P1_NxW", "HIGH"
    p2 = _P2.findall(d)
    if p2:
        w, unit, n = p2[-1]; kg = _to_g(float(w), unit)*float(n)/1000.0
        if _MIN <= kg <= _MAX: return kg, "P2_WxN", "HIGH"
    p4 = _P4.findall(d)
    if p4:
        w, unit, n = p4[-1]; kg = _to_g(float(w), unit)*float(n)/1000.0
        if _MIN <= kg <= _MAX: return kg, "P4_PAREN", "MEDIUM"
    return None, None, None


# ================================================================
# STAGE 2 — COLUMN AUTO-DETECT FOR IMPUTATION
# ================================================================
IMP_COL_CANDIDATES = {
    "col_mt":         ["MT", "MT_WEIGHT", "TOTAL_MT", "NET_WEIGHT_MT", "WEIGHT_MT", "MT WEIGHT"],
    "col_mt_status":  ["MT_STATUS", "MT_CONVERSION_STATUS", "CONVERSION_STATUS"],
    "col_fob":        ["FOB Value (USD)", "FOB_VALUE_USD", "FOB VALUE (USD)", "FOB VALUE", "FOB", "VALUE (USD)"],
    "col_unit":       ["Unit", "UNIT", "UOM", "STANDARD QUANTITY UNIT", "QTY UNIT"],
    "col_qty":        ["Quantity", "QUANTITY", "QTY", "STANDARD QUANTITY"],
    "col_desc":       ["Product Description", "PRODUCT DESCRIPTION", "PRODUCT_DESCRIPTION", "DESCRIPTION"],
    "col_hs":         ["HS Code", "HS_CODE", "HSCODE", "HS CODE", "HSN CODE"],
    "col_port":       ["Port", "PORT", "PORT OF EXPORT", "ORIGIN PORT", "LOADING PORT"],
    "col_exporter":   ["Exporter Name", "EXPORTER_NAME", "EXPORTER NAME", "EXPORTER", "SHIPPER"],
    "col_unit_price": ["Unit Price (USD)", "UNIT_PRICE_USD", "UNIT PRICE (USD)", "UNIT PRICE"],
    "col_date":       ["Shipment Date", "SHIPMENT_DATE", "SHIPMENT DATE", "DATE", "SB DATE"],
}

def resolve_imp_columns(df):
    actual_lower = {c.strip().lower(): c.strip() for c in df.columns}
    resolved = {}
    for cfg_key, candidates in IMP_COL_CANDIDATES.items():
        matched = None
        for candidate in candidates:
            if candidate.strip().lower() in actual_lower:
                matched = actual_lower[candidate.strip().lower()]; break
        if matched is None:
            for candidate in candidates:
                cl = candidate.strip().lower()
                for al, ao in actual_lower.items():
                    if cl in al or al in cl:
                        matched = ao; break
                if matched: break
        resolved[cfg_key] = matched
    return resolved


# ================================================================
# STAGE 2 — TIER 1 IMPUTATION
# ================================================================
def imp_tier1(row, cols, cfg):
    qty_col = cols.get("col_qty"); unit_col = cols.get("col_unit")
    fob_col = cols.get("col_fob"); up_col   = cols.get("col_unit_price")
    if not qty_col or not unit_col: return None
    qty = row.get(qty_col); unit_raw = str(row.get(unit_col, "")).strip().upper()
    if pd.isna(qty) or float(qty) <= 0: return None
    qty = float(qty)
    canonical = parse_unit_canonical(unit_raw)
    if canonical in WEIGHT_UNIT_MAP:
        mt_est = qty * WEIGHT_UNIT_MAP[canonical]
        fob    = row.get(fob_col) if fob_col else None
        flag   = "T1_UNIT_CONVERT" if (pd.notna(fob) and fob > 0) else "T1_UNIT_CONVERT_ZERO_FOB"
        return (mt_est, flag, mt_est * 0.95, mt_est * 1.05)
    if canonical in ("BAG", "SACK"):
        up = row.get(up_col) if up_col else None
        bkg = bag_weight_from_unit_price(up)
        mt_est = qty * bkg / 1000.0
        return (mt_est, "T1_UNIT_CONVERT", qty * 0.050, qty * 0.060)
    for key in ["FIBC", "BIG BAG", "JUMBO", "SUPER", "TEU", "20FT", "CONTAINER", "40FT", "FTE"]:
        if canonical in (key,):
            bm_key = "JUMBO" if canonical in ("SUPER",) else \
                     "FIBC"  if canonical in ("BIG BAG",) else canonical
            central, lo_kg, hi_kg = PACKAGING_BENCHMARKS.get(bm_key, PACKAGING_BENCHMARKS["TEU"])
            return (qty * central, "T1_UNIT_CONVERT", qty * lo_kg, qty * hi_kg)
    return None

def imp_tier1b(row, cols, cfg):
    qty_col = cols.get("col_qty"); desc_col = cols.get("col_desc")
    if not qty_col or not desc_col: return None
    qty = row.get(qty_col); desc = row.get(desc_col, "")
    if pd.isna(qty): return None
    qty = float(qty); qty_is_zero = (qty == 0)
    if qty_is_zero:
        kg_per_ctn, pattern, confidence = extract_carton_weight_kg(desc)
        if kg_per_ctn is None: return None
        mt_est = kg_per_ctn / 1000.0
        return (mt_est, f"T1B_DESC_{pattern}_ZERO_QTY", mt_est * 0.80, mt_est * 1.20)
    if qty <= 0: return None
    kg_per_ctn, pattern, confidence = extract_carton_weight_kg(desc)
    if kg_per_ctn is None: return None
    mt_est = qty * kg_per_ctn / 1000.0
    if mt_est < cfg["min_plausible_mt"] or mt_est > cfg["max_plausible_mt"]: return None
    lo, hi = (mt_est * 0.95, mt_est * 1.05) if confidence == "HIGH" else (mt_est * 0.85, mt_est * 1.15)
    return (mt_est, f"T1B_DESC_{pattern}", lo, hi)

def _desc_tokens_imp(desc):
    if not desc or (isinstance(desc, float) and np.isnan(desc)): return set()
    tokens = re.sub(r'[^A-Z0-9\s]', ' ', str(desc).upper()).split()
    return {t for t in tokens if len(t) >= 3 and t not in _STOP_WORDS_PEER}

def _desc_similarity_imp(a, b):
    ta, tb = _desc_tokens_imp(a), _desc_tokens_imp(b)
    if not ta or not tb: return 0.0
    return len(ta & tb) / len(ta | tb)

def build_peer_index_imp(df, cols):
    col_mt = cols.get("col_mt"); col_qty = cols.get("col_qty")
    col_exp = cols.get("col_exporter"); col_port = cols.get("col_port")
    col_hs = cols.get("col_hs"); col_desc = cols.get("col_desc")
    col_date = cols.get("col_date"); col_unit = cols.get("col_unit")
    if not all([col_mt, col_qty, col_exp, col_port, col_hs, col_desc]):
        return {}, {}
    base = df[df[col_mt].notna() & (df[col_mt] > 0) & df[col_qty].notna() & (df[col_qty] > 0)].copy()
    if base.empty or not col_date or col_date not in base.columns: return {}, {}
    base["_period"] = pd.to_datetime(base[col_date], errors="coerce").dt.to_period("M")
    base["_hs6"]    = base[col_hs].apply(lambda x: get_hs_prefix(x, 6))
    base["_mpu"]    = base[col_mt] / base[col_qty]
    exp_index = {}; port_index = {}
    for _, r in base.iterrows():
        entry = (r["_period"], r[col_desc], r["_mpu"], r.get(col_unit, ""))
        key_exp  = (str(r[col_exp]).strip(),  r["_hs6"])
        key_port = (str(r.get(col_port, "")).strip(), r["_hs6"])
        exp_index.setdefault(key_exp, []).append(entry)
        port_index.setdefault(key_port, []).append(entry)
    return exp_index, port_index

def imp_tier1c(row, exp_index, port_index, cols, cfg):
    desc_col = cols.get("col_desc"); qty_col = cols.get("col_qty")
    exp_col  = cols.get("col_exporter"); port_col = cols.get("col_port")
    hs_col   = cols.get("col_hs"); date_col = cols.get("col_date")
    desc = row.get(desc_col, "") if desc_col else ""
    if not any(b in str(desc).upper() for b in _BRAND_KEYWORDS): return None
    if not qty_col: return None
    qty = row.get(qty_col)
    if pd.isna(qty) or float(qty) <= 0: return None
    qty = float(qty)
    hs6  = get_hs_prefix(row.get(hs_col, ""), 6) if hs_col else ""
    exp  = str(row.get(exp_col, "")).strip()  if exp_col else ""
    port = str(row.get(port_col, "")).strip() if port_col else ""
    try:
        target_period = pd.Period(row[date_col], "M") if (date_col and date_col in row and pd.notna(row.get(date_col))) else None
    except: target_period = None
    def _gap(p):
        if target_period is None or p is None: return 999
        try: return abs((p - target_period).n)
        except: return 999
    desc_tokens = _desc_tokens_imp(desc)
    is_bare = len(desc_tokens) <= 2
    matched_brands = [b for b in _BRAND_KEYWORDS if b in str(desc).upper()]
    best_score, best_mpu, best_source = -1, None, None
    for key, src_label in [((exp, hs6), "exporter"), ((port, hs6), "port")]:
        index = exp_index if src_label == "exporter" else port_index
        candidates = index.get(key, [])
        if is_bare:
            brand_mpus = []
            for period, peer_desc, mpu, _ in candidates:
                if _gap(period) > 3: continue
                if any(b in str(peer_desc).upper() for b in matched_brands) and mpu and mpu > 0:
                    brand_mpus.append(mpu)
            if brand_mpus:
                med = float(np.median(brand_mpus))
                if med > (best_mpu if best_mpu else 0):
                    best_score, best_mpu, best_source = 0.3, med, src_label + "_BARE"
        else:
            for period, peer_desc, mpu, _ in candidates:
                gap = _gap(period)
                if gap > 3: continue
                sim = _desc_similarity_imp(desc, peer_desc)
                if sim < 0.35: continue
                score = sim * max(0.4, 1.0 - gap * 0.15)
                if score > best_score:
                    best_score, best_mpu, best_source = score, mpu, src_label
    if best_mpu is None or best_mpu <= 0: return None
    mt_est = qty * best_mpu
    if mt_est < cfg["min_plausible_mt"] or mt_est > cfg["max_plausible_mt"]: return None
    if "BARE" in str(best_source):
        lo, hi = mt_est * 0.60, mt_est * 1.40
        flag = f"T1C_PEER_{best_source.replace('_BARE','').upper()}_BARE_BRAND"
    else:
        margin = 0.15 if "exporter" in best_source else 0.25
        lo, hi = mt_est * (1 - margin), mt_est * (1 + margin)
        flag = f"T1C_PEER_{best_source.upper()}"
    return mt_est, flag, lo, hi

def build_suv_table_imp(df, cols, cfg):
    col_mt = cols.get("col_mt"); col_fob = cols.get("col_fob")
    col_hs = cols.get("col_hs"); col_port = cols.get("col_port")
    col_date = cols.get("col_date")
    if not all([col_mt, col_fob, col_hs, col_port]): return {"hs6": {}}
    base = df[df[col_mt].notna() & (df[col_mt] > 0) & df[col_fob].notna() & (df[col_fob] > 0)].copy()
    if base.empty: return {"hs6": {}}
    base["_uv"]  = base[col_fob] / base[col_mt]
    base["_hs6"] = base[col_hs].apply(lambda x: get_hs_prefix(x, 6))
    if col_date and col_date in base.columns and base[col_date].notna().any():
        base["_period"] = pd.to_datetime(base[col_date], errors="coerce").dt.to_period("M").astype(str)
    else:
        base["_period"] = "ALL"
    suv_table = {"hs6": {}}
    for (hs6, port, period), grp in base.groupby(["_hs6", col_port, "_period"]):
        uv = grp["_uv"].dropna(); uv = uv[(uv > 0) & np.isfinite(uv)]
        n = len(uv)
        if n < cfg["suv_min_obs_low"]: continue
        med = float(np.median(uv)); std = float(np.std(uv)) if n > 1 else 0.0
        cv  = std / med if med > 0 else 999
        rel = "HIGH" if (n >= cfg["suv_min_obs_high"] and cv < 0.3) else \
              "MEDIUM" if (n >= cfg["suv_min_obs_high"] and cv < 0.5) else "LOW"
        suv_table["hs6"][(hs6, port, period)] = {"suv": med, "n_obs": n, "reliability": rel}
    return suv_table

def imp_tier2(row, suv_table, cols, cfg):
    fob_col = cols.get("col_fob"); hs_col = cols.get("col_hs")
    port_col = cols.get("col_port"); date_col = cols.get("col_date")
    if not fob_col: return None
    fob = row.get(fob_col)
    if pd.isna(fob) or fob <= 0: return None
    hs6  = get_hs_prefix(row.get(hs_col, ""), 6) if hs_col else ""
    port = str(row.get(port_col, "")).strip() if port_col else ""
    try:
        period = pd.Period(row[date_col], "M").strftime("%Y-%m") if (date_col and pd.notna(row.get(date_col))) else "ALL"
    except: period = "ALL"
    key = (hs6, port, period)
    entry = suv_table["hs6"].get(key)
    if entry is None:
        for (h, p, per), e in suv_table["hs6"].items():
            if h == hs6 and per == period and e["n_obs"] >= cfg["suv_min_obs_low"]:
                entry = e; break
    if entry is None: return None
    suv = entry["suv"]
    if suv <= 0: return None
    mt_est = fob / suv
    if mt_est < cfg["min_plausible_mt"] or mt_est > cfg["max_plausible_mt"]: return None
    std_g = suv * 0.3
    lo = fob / (suv + std_g); hi = fob / max(suv - std_g, suv * 0.1)
    return (mt_est, "T2_SUV_HS6", suv, entry["n_obs"], "hs6", lo, hi)

def build_temporal_index_imp(df, cols):
    col_mt = cols.get("col_mt"); col_exp = cols.get("col_exporter")
    col_hs = cols.get("col_hs"); col_date = cols.get("col_date")
    if not all([col_mt, col_exp, col_hs, col_date]) or col_date not in df.columns:
        return {}
    base = df[df[col_mt].notna() & (df[col_mt] > 0)].copy()
    base["_period"] = pd.to_datetime(base[col_date], errors="coerce").dt.to_period("M")
    base["_hs4"]    = base[col_hs].apply(lambda x: get_hs_prefix(x, 4))
    temporal = {}
    for (exp, hs4), grp in base.groupby([col_exp, "_hs4"]):
        temporal[(str(exp).strip(), hs4)] = grp.groupby("_period")[col_mt].median().sort_index()
    return temporal

def imp_tier3(row, temporal_idx, cols, cfg):
    col_exp = cols.get("col_exporter"); col_hs = cols.get("col_hs")
    col_fob = cols.get("col_fob"); col_date = cols.get("col_date")
    exp = str(row.get(col_exp, "")).strip() if col_exp else ""
    hs4 = get_hs_prefix(row.get(col_hs, ""), 4) if col_hs else ""
    fob = row.get(col_fob) if col_fob else None
    if col_date and col_date in row and pd.notna(row.get(col_date)):
        key = (exp, hs4)
        if key in temporal_idx:
            try:
                target = pd.Period(row[col_date], "M")
                diffs  = [(abs((p - target).n), p, v) for p, v in temporal_idx[key].items() if abs((p - target).n) <= 3]
                if diffs:
                    diffs.sort()
                    _, _, nearest_mt = diffs[0]
                    mt_est = nearest_mt * max(0.5, 1.0 - diffs[0][0] * 0.1)
                    return (mt_est, "T3_INTERPOLATED", None, 0, "temporal", mt_est * 0.7, mt_est * 1.3)
            except: pass
    if fob is not None and pd.notna(fob) and fob > 0:
        hs_val = row.get(col_hs, "") if col_hs else ""
        group  = detect_hs_ico_group(hs_val)
        ico_suv = ICO_PRICES.get(group, ICO_PRICES["DEFAULT"])
        mt_est  = fob / ico_suv
        if cfg["min_plausible_mt"] <= mt_est <= cfg["max_plausible_mt"]:
            return (mt_est, "T3_ICO_ANCHOR", ico_suv, 0, "ico", mt_est * 0.6, mt_est * 1.4)
    return (None, "IRRECOVERABLE", None, 0, None, None, None)


# ================================================================
# STAGE 2 — MAIN IMPUTATION RUNNER
# ================================================================
def run_imputation(df_input):
    """Run MT imputation on a cleaned dataframe. Returns (df_imputed, counts_dict)."""
    df = df_input.copy()
    cols = resolve_imp_columns(df)
    cfg  = IMP_CFG.copy()

    col_mt   = cols.get("col_mt")
    col_date = cols.get("col_date")

    if not col_mt or col_mt not in df.columns:
        # Try to find MT column from the cleaned output (may be named 'MT')
        for candidate in ["MT", "MT_WEIGHT", "TOTAL_MT", "NET_WEIGHT_MT"]:
            if candidate in df.columns:
                col_mt = candidate
                cols["col_mt"] = candidate
                break
        if not col_mt:
            return df, {"error": "MT column not found"}

    # Ensure date column is parsed
    if col_date and col_date in df.columns:
        df[col_date] = pd.to_datetime(df[col_date], errors="coerce")

    # Init output columns
    df["MT_weight_final"] = np.nan
    df["MT_FLAG"]         = ""
    df["MT_source_tier"]  = -1
    df["SUV_used"]        = np.nan
    df["SUV_n_obs"]       = np.nan
    df["MT_lower_bound"]  = np.nan
    df["MT_upper_bound"]  = np.nan

    # Mark observed rows
    has_mt = df[col_mt].notna() & (df[col_mt] > 0)
    df.loc[has_mt, "MT_weight_final"] = df.loc[has_mt, col_mt]
    df.loc[has_mt, "MT_FLAG"]         = "OBSERVED"
    df.loc[has_mt, "MT_source_tier"]  = 0

    # Build reference structures
    suv_table    = build_suv_table_imp(df, cols, cfg)
    exp_idx, port_idx = build_peer_index_imp(df, cols)
    temporal_idx = build_temporal_index_imp(df, cols)

    # Identify blank rows
    blank_mask = df[col_mt].isna() | (df[col_mt] == 0)
    col_status = cols.get("col_mt_status")
    if col_status and col_status in df.columns:
        blank_mask = blank_mask | (df[col_status].astype(str).str.strip().str.upper() == "BLANK")

    counts = {"OBSERVED": int(has_mt.sum()), "T1": 0, "T1B": 0, "T1C": 0, "T2": 0, "T3": 0, "IRRECOVERABLE": 0}

    for idx, row in df[blank_mask].iterrows():
        t1 = imp_tier1(row, cols, cfg)
        if t1:
            mt_est, flag, lo, hi = t1
            df.at[idx, "MT_weight_final"] = mt_est; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_source_tier"]  = 1;      df.at[idx, "MT_lower_bound"] = lo; df.at[idx, "MT_upper_bound"] = hi
            counts["T1"] += 1; continue

        t1b = imp_tier1b(row, cols, cfg)
        if t1b:
            mt_est, flag, lo, hi = t1b
            df.at[idx, "MT_weight_final"] = mt_est; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_source_tier"]  = 1;      df.at[idx, "MT_lower_bound"] = lo; df.at[idx, "MT_upper_bound"] = hi
            counts["T1B"] += 1; continue

        t1c = imp_tier1c(row, exp_idx, port_idx, cols, cfg)
        if t1c:
            mt_est, flag, lo, hi = t1c
            df.at[idx, "MT_weight_final"] = mt_est; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_source_tier"]  = 1;      df.at[idx, "MT_lower_bound"] = lo; df.at[idx, "MT_upper_bound"] = hi
            counts["T1C"] += 1; continue

        t2 = imp_tier2(row, suv_table, cols, cfg)
        if t2:
            mt_est, flag, suv, n_obs, hs_lvl, lo, hi = t2
            df.at[idx, "MT_weight_final"] = mt_est; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_source_tier"]  = 2;      df.at[idx, "SUV_used"] = suv; df.at[idx, "SUV_n_obs"] = n_obs
            df.at[idx, "MT_lower_bound"]  = lo;     df.at[idx, "MT_upper_bound"] = hi
            counts["T2"] += 1; continue

        t3 = imp_tier3(row, temporal_idx, cols, cfg)
        mt_est, flag, suv, n_obs, hs_lvl, lo, hi = t3
        if flag == "IRRECOVERABLE":
            df.at[idx, "MT_FLAG"] = "IRRECOVERABLE"; df.at[idx, "MT_source_tier"] = 3
            counts["IRRECOVERABLE"] += 1
        else:
            df.at[idx, "MT_weight_final"] = mt_est; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_source_tier"]  = 3;      df.at[idx, "SUV_used"] = suv; df.at[idx, "SUV_n_obs"] = n_obs
            df.at[idx, "MT_lower_bound"]  = lo;     df.at[idx, "MT_upper_bound"] = hi
            counts["T3"] += 1

    return df, counts

def write_imputed_excel(df_imp, counts):
    """Write MT_IMPUTED excel with two sheets: Data + Summary."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_imp.to_excel(writer, sheet_name='MT Imputed Data', index=False)
        wb = writer.book; ws = writer.sheets['MT Imputed Data']
        hdr_fmt = wb.add_format({'bold': True, 'bg_color': '#0D3B66', 'font_color': '#FFFFFF',
                                  'border': 1, 'font_size': 10, 'align': 'center'})
        row1_fmt = wb.add_format({'bg_color': '#D6E4F0', 'border': 1, 'font_size': 9})
        row2_fmt = wb.add_format({'bg_color': '#EBF4FA', 'border': 1, 'font_size': 9})
        for ci, cn in enumerate(df_imp.columns):
            ws.write(0, ci, cn, hdr_fmt)
        for ri in range(1, len(df_imp) + 1):
            ws.set_row(ri, None, row1_fmt if ri % 2 == 1 else row2_fmt)
        for ci, cn in enumerate(df_imp.columns):
            ws.set_column(ci, ci, min(max(len(str(cn)) + 4, 10), 40))
        ws.freeze_panes(1, 0)

        flag_counts = df_imp["MT_FLAG"].value_counts()
        summary_rows = [{"Flag": k, "Count": v} for k, v in flag_counts.items()]
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_excel(writer, sheet_name='Imputation Summary', index=False)
        ws2 = writer.sheets['Imputation Summary']
        for ci, cn in enumerate(summary_df.columns):
            ws2.write(0, ci, cn, hdr_fmt)
        ws2.set_column(0, 0, 30); ws2.set_column(1, 1, 12)
    buf.seek(0)
    return buf.getvalue()


# ================================================================
# STAGE 1 — PROCESS FILE
# ================================================================
DROP_COLS = ['_HSN_INT', '_DESC_UP', '_BUCKET', '_EXCLUDED', '_EXCL_REASON',
             '_IS_CHICORY_SIGNAL', '_WRONG_SOLUBLE', '_WRONG_CHICORY', '_WRONG_ANY',
             '_SOURCE_TEMP']

def clean_export(df_in):
    keep = [c for c in df_in.columns if c not in DROP_COLS]
    return df_in[keep].reset_index(drop=True)

def process_file(file, excl_df_json):
    try:    df = pd.read_excel(file, engine='calamine')
    except: df = pd.read_excel(file, engine='openpyxl')
    df.columns = df.columns.str.strip()

    hs_col   = next((c for c in df.columns if 'HS' in c.upper() and 'CODE' in c.upper()), None)
    if not hs_col: hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)
    desc_col = next((c for c in df.columns if 'PRODUCT' in c.upper() and 'DESC' in c.upper()), None)
    if not desc_col: desc_col = next((c for c in df.columns if 'DESC' in c.upper()), None)

    if not hs_col or not desc_col:
        st.error(f"Could not find HS CODE or PRODUCT DESCRIPTION columns in {file.name}")
        return None

    df['_HSN_INT'] = norm_hsn_series(df[hs_col])
    df['_DESC_UP'] = df[desc_col].astype(str).str.upper().str.strip()
    df['_BUCKET']  = bucket_hsn_series(df['_HSN_INT'])

    excl_global_kws, excl_hsn_kws = build_excl_list_lookup(excl_df_json)
    df['_EXCLUDED'], df['_EXCL_REASON'] = apply_exclusions_vectorised(df, excl_global_kws, excl_hsn_kws)

    df_wrong   = find_wrong_hsn_rows(df, hs_col)
    df_wrong   = df_wrong[~df_wrong['_EXCLUDED']].copy()
    df_correct = df[df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX']) & ~df['_EXCLUDED']].copy()
    df_sheet1  = pd.concat([df_correct, df_wrong], ignore_index=True)
    df_sheet1['MT'], df_sheet1['MT_STATUS'] = convert_to_mt_vectorised(df_sheet1)
    df_sheet1['_IS_CHICORY_SIGNAL'] = df_sheet1['_DESC_UP'].str.contains(CHICORY_SIGNAL_PATTERN, na=False, regex=True)

    df_chicory_pool = df_sheet1[df_sheet1['_IS_CHICORY_SIGNAL']].copy()

    def apply_classification(df_in):
        results = df_in['_DESC_UP'].apply(classify_chicory_row)
        df_in = df_in.copy()
        df_in['BLEND_CATEGORY'] = results.apply(lambda x: x[0] if x else 'ASSUMED')
        df_in['COFFEE_PCT']     = results.apply(lambda x: x[1] if x else None)
        df_in['CHICORY_PCT']    = results.apply(lambda x: x[2] if x else None)
        df_in['CONFIDENCE']     = results.apply(lambda x: x[3] if x else 'LOW')
        df_in['BLEND_NOTES']    = results.apply(lambda x: x[4] if x else 'No confirmed ratio')
        return df_in

    df_chicory_pool = apply_classification(df_chicory_pool)
    df_premix = df_sheet1[(df_sheet1['_BUCKET'] == 'CHICORY_PREMIX') & (~df_sheet1.index.isin(df_chicory_pool.index))].copy()
    df_premix = apply_classification(df_premix)
    df_all_chicory = pd.concat([df_chicory_pool, df_premix], ignore_index=True)

    df_chic_explicit = df_all_chicory[df_all_chicory['BLEND_CATEGORY'] == 'EXPLICIT'].copy()
    df_chic_known    = df_all_chicory[df_all_chicory['BLEND_CATEGORY'] == 'KNOWN_BRAND'].copy()
    df_chic_assumed  = df_all_chicory[df_all_chicory['BLEND_CATEGORY'].isin(['ASSUMED', 'PURE_COFFEE'])].copy()

    df_chicory_only = df[df['_BUCKET'] == 'CHICORY_ONLY'].copy()
    if len(df_chicory_only):
        df_chicory_only['MT'], df_chicory_only['MT_STATUS'] = convert_to_mt_vectorised(df_chicory_only)

    df_excl_from_target = df[df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX']) & df['_EXCLUDED']].copy()
    scannable_mask      = ~df['_BUCKET'].isin(['SOLUBLE_COFFEE','CHICORY_PREMIX','CHICORY_ONLY','PURE_CHICORY'])
    df_other            = df[scannable_mask].copy()
    df_other            = df_other[~df_other.index.isin(df_wrong.index)].copy()
    df_excluded_review  = pd.concat([df_excl_from_target, df_other], ignore_index=True)

    summary_df = pd.DataFrame([
        {'Sheet': '1 All Soluble Coffee',     'Rows': len(df_sheet1),        'Notes': 'Correct HSN + wrong HSN rescued rows'},
        {'Sheet': '2 Chicory Explicit Ratio', 'Rows': len(df_chic_explicit), 'Notes': 'Ratio or chicory word in product description'},
        {'Sheet': '3 Chicory Known Brand',    'Rows': len(df_chic_known),    'Notes': 'Matched to brand reference table'},
        {'Sheet': '4 Chicory Assumed',        'Rows': len(df_chic_assumed),  'Notes': 'Chicory signal but no confirmed ratio'},
        {'Sheet': '5 Chicory Only Exports',   'Rows': len(df_chicory_only),  'Notes': 'HSN 21013010 — pure roasted chicory exports'},
        {'Sheet': '6 Excluded Items Review',  'Rows': len(df_excluded_review),'Notes': 'Non-soluble products removed'},
    ])

    return {
        '1 All Soluble Coffee':     clean_export(df_sheet1),
        '2 Chicory Explicit Ratio': clean_export(df_chic_explicit),
        '3 Chicory Known Brand':    clean_export(df_chic_known),
        '4 Chicory Assumed':        clean_export(df_chic_assumed),
        '5 Chicory Only Exports':   clean_export(df_chicory_only),
        '6 Excluded Items Review':  clean_export(df_excluded_review),
        'Summary':                  summary_df,
    }


# ================================================================
# UI — HERO
# ================================================================
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">LDC · Coffee Commercial · SIP 2026</div>
    <h1>Coffee Trade Intelligence</h1>
    <div class="hero-sub">UPLOAD → CLEAN → CONVERT → IMPUTE → DOWNLOAD</div>
</div>
""", unsafe_allow_html=True)


# ================================================================
# UI — STAGE 1: EXCLUSION LIST
# ================================================================
st.markdown("""
<div class="stage-header">
    <span class="stage-num">STAGE 01</span>
    <span class="stage-title">Exclusion List</span>
</div>
""", unsafe_allow_html=True)
excl = st.file_uploader("Upload exclusion list (.xlsx with KEYWORD column)", type=["xlsx"], key="excl")


# ================================================================
# UI — STAGE 2: RAW DATA
# ================================================================
st.markdown("""
<div class="stage-header">
    <span class="stage-num">STAGE 02</span>
    <span class="stage-title">Raw CYBEX Files</span>
</div>
""", unsafe_allow_html=True)
raws = st.file_uploader("Upload one or more raw CYBEX export files", type=["xlsx"], accept_multiple_files=True, key="raws")

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("▶  Run Pipeline", use_container_width=False)

# ================================================================
# UI — PIPELINE EXECUTION
# ================================================================
if run_btn:
    if not excl:
        st.error("Please upload an exclusion list first.")
    elif not raws:
        st.error("Please upload at least one raw file.")
    else:
        excl_df = pd.read_excel(excl)
        excl_df.columns = excl_df.columns.str.strip().str.upper()
        if 'KEYWORD' not in excl_df.columns:
            st.error("Exclusion list must have a KEYWORD column.")
        else:
            excl_df_json = excl_df.to_json()

            for f in raws:
                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="stage-header">
                    <span class="stage-num">PROCESSING</span>
                    <span class="stage-title">{f.name}</span>
                </div>
                """, unsafe_allow_html=True)

                # ── STAGE 1: CLEAN ──
                with st.spinner(f"Stage 1 — Cleaning & classifying..."):
                    result = process_file(f, excl_df_json)

                if result is None:
                    continue

                st.success(f"✓ Stage 1 complete — {f.name}")
                st.dataframe(result['Summary'], use_container_width=True, hide_index=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    try:
                        excel_bytes = write_excel(result)
                        st.download_button(
                            label="⬇  Download CLEANED file (Sheets 1–5)",
                            data=excel_bytes,
                            file_name=f"CLEANED_{f.name}",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_clean_{f.name}"
                        )
                    except Exception as e:
                        st.error(f"Excel generation failed: {e}")
                with col_dl2:
                    excl_sheet = result.get('6 Excluded Items Review')
                    if excl_sheet is not None and len(excl_sheet):
                        csv_bytes = excl_sheet.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"⬇  Download Excluded Items ({len(excl_sheet):,} rows) CSV",
                            data=csv_bytes,
                            file_name=f"EXCLUDED_{f.name.replace('.xlsx','.csv')}",
                            mime="text/csv",
                            key=f"dl_excl_{f.name}"
                        )

                # ── STAGE 2: IMPUTE ──
                st.markdown("""
                <div class="stage-header" style="margin-top:32px">
                    <span class="stage-num">STAGE 03</span>
                    <span class="stage-title">MT Weight Imputation</span>
                </div>
                """, unsafe_allow_html=True)

                df_soluble = result.get('1 All Soluble Coffee')
                if df_soluble is None or len(df_soluble) == 0:
                    st.warning("No soluble coffee rows found — skipping imputation.")
                    continue

                with st.spinner("Running three-tier imputation framework..."):
                    df_imputed, counts = run_imputation(df_soluble)

                if "error" in counts:
                    st.error(f"Imputation error: {counts['error']}")
                    continue

                st.success(f"✓ Stage 3 complete — MT imputation done")

                # ── TIER BREAKDOWN CARDS ──
                total_rows = sum(v for k, v in counts.items() if k != "error")

                def pct(n):
                    return f"{n/total_rows*100:.1f}%" if total_rows > 0 else "—"

                tier_configs = [
                    ("OBSERVED",      counts.get("OBSERVED", 0),     "observed",  "Ground Truth"),
                    ("TIER 1",        counts.get("T1", 0),           "tier1",     "Direct Convert"),
                    ("TIER 1B",       counts.get("T1B", 0),          "tier1b",    "Carton Pattern"),
                    ("TIER 1C",       counts.get("T1C", 0),          "tier1c",    "Brand Peer"),
                    ("TIER 2",        counts.get("T2", 0),           "tier2",     "SUV Estimate"),
                    ("TIER 3",        counts.get("T3", 0),           "tier3",     "ICO / Temporal"),
                    ("UNRESOLVED",    counts.get("IRRECOVERABLE", 0),"irrecov",   "Irrecoverable"),
                ]

                cards_html = '<div class="tier-grid">'
                for label, count, cls, sublabel in tier_configs:
                    cards_html += f"""
                    <div class="tier-card {cls}">
                        <div class="tier-label">{label}</div>
                        <div class="tier-count">{count:,}</div>
                        <div class="tier-pct">{pct(count)} · {sublabel}</div>
                    </div>"""
                cards_html += '</div>'
                st.markdown(cards_html, unsafe_allow_html=True)

                # ── STACKED PROGRESS BAR ──
                colors = {"OBSERVED": "#00d4aa", "T1": "#3b82f6", "T1B": "#8b5cf6",
                          "T1C": "#a78bfa", "T2": "#f59e0b", "T3": "#ef4444", "IRRECOVERABLE": "#374151"}
                bar_html = '<div class="tier-bar-wrap">'
                for key, color in colors.items():
                    n = counts.get(key, 0)
                    w = (n / total_rows * 100) if total_rows > 0 else 0
                    if w > 0:
                        bar_html += f'<div class="tier-bar-seg" style="width:{w:.2f}%;background:{color}"></div>'
                bar_html += '</div>'
                st.markdown(bar_html, unsafe_allow_html=True)

                # ── MT TOTALS ──
                mt_col = "MT_weight_final"
                if mt_col in df_imputed.columns:
                    obs_mask = df_imputed["MT_FLAG"] == "OBSERVED"
                    mt_obs   = df_imputed.loc[obs_mask, mt_col].sum()
                    mt_all   = df_imputed[mt_col].sum()
                    mt_imp   = mt_all - mt_obs
                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        st.markdown(f"""
                        <div class="result-box">
                            <div class="result-box-label">Observed MT</div>
                            <div class="result-mt">{mt_obs:,.1f}</div>
                            <div class="result-mt-sub">ground truth weight</div>
                        </div>""", unsafe_allow_html=True)
                    with rc2:
                        st.markdown(f"""
                        <div class="result-box">
                            <div class="result-box-label">Imputed MT</div>
                            <div class="result-mt">{mt_imp:,.1f}</div>
                            <div class="result-mt-sub">estimated by pipeline</div>
                        </div>""", unsafe_allow_html=True)
                    with rc3:
                        st.markdown(f"""
                        <div class="result-box">
                            <div class="result-box-label">Total MT</div>
                            <div class="result-mt">{mt_all:,.1f}</div>
                            <div class="result-mt-sub">all rows combined</div>
                        </div>""", unsafe_allow_html=True)

                # ── DOWNLOADS ──
                st.markdown("<br>", unsafe_allow_html=True)
                imp_col1, imp_col2 = st.columns(2)
                with imp_col1:
                    try:
                        imp_bytes = write_imputed_excel(df_imputed, counts)
                        st.download_button(
                            label=f"⬇  Download MT_IMPUTED_{f.name}",
                            data=imp_bytes,
                            file_name=f"MT_IMPUTED_{f.name}",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_imp_{f.name}"
                        )
                    except Exception as e:
                        st.error(f"Imputed Excel failed: {e}")
                with imp_col2:
                    summary_data = [
                        {"Tier": "OBSERVED",      "Count": counts.get("OBSERVED", 0),     "Method": "Ground truth MT values"},
                        {"Tier": "T1",            "Count": counts.get("T1", 0),           "Method": "Direct unit conversion"},
                        {"Tier": "T1B",           "Count": counts.get("T1B", 0),          "Method": "Description carton weight"},
                        {"Tier": "T1C",           "Count": counts.get("T1C", 0),          "Method": "Named-brand peer lookup"},
                        {"Tier": "T2",            "Count": counts.get("T2", 0),           "Method": "SUV (HS6 + port + period)"},
                        {"Tier": "T3",            "Count": counts.get("T3", 0),           "Method": "ICO anchor / temporal interp"},
                        {"Tier": "IRRECOVERABLE", "Count": counts.get("IRRECOVERABLE", 0),"Method": "No recovery possible — excluded"},
                    ]
                    summary_csv = pd.DataFrame(summary_data).to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇  Download Imputation Summary (CSV)",
                        data=summary_csv,
                        file_name=f"IMPUTATION_SUMMARY_{f.name.replace('.xlsx','.csv')}",
                        mime="text/csv",
                        key=f"dl_impsumm_{f.name}"
                    )
