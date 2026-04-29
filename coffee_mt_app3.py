import streamlit as st
import pandas as pd
import numpy as np
import io
import re
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# ================================================================
# PAGE CONFIG & CSS
# ================================================================
st.set_page_config(page_title="Coffee Trade Intelligence", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');
* { box-sizing: border-box; }
.stApp { background: #050a0f; color: #e2e8f0; font-family: 'Syne', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }

.hero {
    position: relative; overflow: hidden;
    padding: 60px 48px 52px; margin-bottom: 48px;
    border-radius: 2px; background: #050a0f; border-left: 3px solid #00d4aa;
}
.hero::before {
    content: ''; position: absolute; top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(0,212,170,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace; font-size: 11px;
    letter-spacing: 0.22em; color: #00d4aa; text-transform: uppercase; margin-bottom: 16px;
}
.hero h1 {
    font-size: 44px; font-weight: 800; line-height: 1.05;
    margin: 0 0 16px 0; color: #f8fafc; letter-spacing: -0.02em;
}
.hero-sub { font-family: 'DM Mono', monospace; font-size: 13px; color: #64748b; letter-spacing: 0.04em; }

.stage-header { display: flex; align-items: center; gap: 14px; margin: 36px 0 18px 0; }
.stage-num {
    font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.18em;
    color: #00d4aa; border: 1px solid #00d4aa22; padding: 4px 10px;
    border-radius: 2px; background: #00d4aa08;
}
.stage-title { font-size: 18px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.01em; }

.sheet-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 24px 0; }
.sheet-card {
    background: #0d1520; border: 1px solid #1e2d3d; border-radius: 2px;
    padding: 20px 18px; position: relative; overflow: hidden;
}
.sheet-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.sheet-card.s1::before { background: #00d4aa; }
.sheet-card.s2::before { background: #3b82f6; }
.sheet-card.s3::before { background: #f59e0b; }
.sheet-card.s4::before { background: #a78bfa; }
.sheet-label {
    font-family: 'DM Mono', monospace; font-size: 9px;
    letter-spacing: 0.2em; text-transform: uppercase; color: #64748b; margin-bottom: 8px;
}
.sheet-count { font-size: 32px; font-weight: 800; color: #f8fafc; line-height: 1; }
.sheet-name { font-family: 'DM Mono', monospace; font-size: 10px; color: #475569; margin-top: 6px; line-height: 1.4; }

.tier-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 20px 0; }
.tier-card {
    background: #0d1520; border: 1px solid #1e2d3d; border-radius: 2px;
    padding: 16px 14px; position: relative; overflow: hidden;
}
.tier-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.tier-card.observed::before { background: #00d4aa; }
.tier-card.tier1::before    { background: #3b82f6; }
.tier-card.tier1b::before   { background: #8b5cf6; }
.tier-card.tier1c::before   { background: #a78bfa; }
.tier-card.tier2::before    { background: #f59e0b; }
.tier-card.tier3::before    { background: #ef4444; }
.tier-card.irrecov::before  { background: #374151; }
.tier-label { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: #64748b; margin-bottom: 6px; }
.tier-count { font-size: 26px; font-weight: 800; color: #f8fafc; line-height: 1; }
.tier-pct   { font-family: 'DM Mono', monospace; font-size: 10px; color: #475569; margin-top: 4px; }

.tier-bar-wrap { height: 5px; background: #0d1520; border-radius: 1px; overflow: hidden; display: flex; margin: 16px 0 20px; }
.tier-bar-seg  { height: 100%; }

.result-box { background: #0a1525; border: 1px solid #1e2d3d; border-radius: 2px; padding: 20px 24px; margin: 8px 0; }
.result-box-label { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.18em; color: #00d4aa; text-transform: uppercase; margin-bottom: 6px; }
.result-mt     { font-size: 26px; font-weight: 800; color: #f8fafc; }
.result-mt-sub { font-family: 'DM Mono', monospace; font-size: 10px; color: #475569; margin-top: 4px; }

.stButton > button {
    background: #00d4aa !important; color: #050a0f !important; border: none !important;
    border-radius: 2px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    letter-spacing: 0.04em !important; padding: 10px 32px !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stDownloadButton > button {
    background: transparent !important; color: #00d4aa !important;
    border: 1px solid #00d4aa44 !important; border-radius: 2px !important;
    font-family: 'DM Mono', monospace !important; font-size: 12px !important;
    letter-spacing: 0.06em !important;
}
.stDownloadButton > button:hover { border-color: #00d4aa !important; }
div[data-testid="stFileUploader"] {
    background: #0d1520 !important; border: 1px dashed #1e2d3d !important;
    border-radius: 2px !important; padding: 8px !important;
}
[data-testid="stSuccess"] {
    background: #00d4aa0d !important; border: 1px solid #00d4aa33 !important;
    border-radius: 2px !important; color: #00d4aa !important;
}
[data-testid="stError"] {
    background: #ef44440d !important; border: 1px solid #ef444433 !important; border-radius: 2px !important;
}
.divider { border: none; border-top: 1px solid #1e2d3d; margin: 40px 0; }
</style>
""", unsafe_allow_html=True)


# ================================================================
# SECTION A — HSN / BUCKET CONSTANTS
# ================================================================

SOLUBLE_COFFEE_HSN = {21011110, 21011120, 21011130, 21011190}
CHICORY_PREMIX_HSN = {21011200}
CHICORY_ONLY_HSN   = {21013010}
TARGET_HSN         = SOLUBLE_COFFEE_HSN | CHICORY_PREMIX_HSN

# Keywords that flag a row as soluble coffee when it appears under a wrong HSN
SOLUBLE_KEYWORDS = [
    'INSTANT COFFEE', 'SOLUBLE COFFEE', 'SPRAY DRIED COFFEE',
    'FREEZE DRIED COFFEE', 'AGGLOMERATED COFFEE', 'AGGLOMERATED INSTANT',
    'FREEZE-DRIED COFFEE', 'SPRAY-DRIED COFFEE', 'COFFEE EXTRACT POWDER',
    'COFFEE PREMIX', 'NESCAFE', 'BRU INSTANT', 'SUNRISE EXTRA',
]
sol_pattern = '|'.join(re.escape(k) for k in SOLUBLE_KEYWORDS)

CHICORY_WRONG_HSN_KEYWORDS = ['CHICORY', 'CHICCORY']
chic_wrong_pat = '|'.join(re.escape(k) for k in CHICORY_WRONG_HSN_KEYWORDS)

_ADMIN_PATTERNS = re.compile(
    r'\b(?:GSTIN(?=\W)|GSTN(?=\W)|GST\s+NO(?=\W)'
    r'|TAX\s+INV(?:OICE)?|INV\s*NO|INVOICE\s*NO'
    r'|ICO\s+SI\s+NUMBER|ICO\s+MARK\s+NO|PERMIT\s+NUMBER'
    r'|REF\s*NO\.?:)',
    re.IGNORECASE,
)
_MERCH_PATTERNS = re.compile(
    r'\b(?:TSHIRT|T-SHIRT|SAMPLING\s+TABLE|PROMOTIONAL\s+MATERIAL)',
    re.IGNORECASE,
)
_STRICT_COFFEE_SIGNAL = re.compile(
    r'COFFEE|CAPPUCCINO|CAPUCCINO|NESCAFE|BRU|LEVISTA|COTHAS|'
    r'CONTINENTAL|NARASUS|TATA COFFEE|CHICORY|PREMIX',
    re.IGNORECASE,
)
STRICT_CHECK_HSNS = {'21011190', '21011200'}

QUANTITY_AWARE_EXCLUSIONS = [
    ('FREE SAMPLE',          0.05, 'FOC sample — below 50 KGS'),
    ('SAMPLE',               0.05, 'Sample shipment — below 50 KGS'),
    ('TEST REPORT',          0.02, 'QC/test sample — below 20 KGS'),
    ('FOR EXHIBITION',       0.10, 'Exhibition goods — below 100 KGS'),
    ('EXHIBITION GOODS',     0.10, 'Exhibition goods — below 100 KGS'),
    ('NO COMMERCIAL VALUE',  0.10, 'Explicitly NCV — below 100 KGS'),
    ('NCV',                  0.10, 'Explicitly NCV'),
    ('NOT FOR SALE',         0.05, 'Not-for-sale — below 50 KGS'),
    ('FREE OF COST',         0.05, 'FOC shipment — below 50 KGS'),
    ('PROMOTIONAL MATERIAL', 0.05, 'Promo material — below 50 KGS'),
    ('GIFT',                 0.02, 'Gift/personal — below 20 KGS'),
    ('PERSONAL USE',         0.02, 'Personal use — not commercial'),
]


# ================================================================
# SECTION B — EXCLUSION LIST
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
    rsn_col = excl_df['REASON'].astype(str)                             if has_rsn else pd.Series(['Exclusion list'] * len(excl_df))
    valid     = kw_col != ''
    is_global = valid & hsn_col.isin(['', 'nan', 'NAN'])
    is_hsn    = valid & ~hsn_col.isin(['', 'nan', 'NAN'])
    for kw, rsn in zip(kw_col[is_global], rsn_col[is_global]):
        global_kws[kw] = rsn
    for kw, hsn, rsn in zip(kw_col[is_hsn], hsn_col[is_hsn], rsn_col[is_hsn]):
        hsn_kws.setdefault(hsn, {})[kw] = rsn
    return global_kws, hsn_kws


def apply_exclusions(df, excl_global_kws, excl_hsn_kws):
    desc  = df['_DESC_UP']
    hsn_s = df['_HSN_STR']

    qty_col  = next((c for c in ['STANDARD QUANTITY', 'QUANTITY', 'QTY'] if c in df.columns), None)
    unit_col = next((c for c in ['STANDARD QUANTITY UNIT', 'UNIT', 'UOM', 'QTY UNIT'] if c in df.columns), None)

    if qty_col:
        raw_qty = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
        if unit_col:
            unit_s = df[unit_col].astype(str).str.strip().str.upper()
            qty_mt = pd.Series(np.nan, index=df.index)
            qty_mt = qty_mt.where(~unit_s.isin(['KGS', 'KG']), raw_qty / 1000)
            qty_mt = qty_mt.where(~unit_s.isin(['MTS', 'MT']), raw_qty)
        else:
            qty_mt = raw_qty / 1000
    else:
        qty_mt = pd.Series(np.nan, index=df.index)

    n        = len(df)
    excluded = np.zeros(n, dtype=bool)
    reason   = np.full(n, '', dtype=object)

    def _mark(bool_series, rsn):
        pos = df.index.get_indexer(bool_series[bool_series].index)
        excluded[pos] = True
        for p in pos:
            if reason[p] == '':
                reason[p] = rsn

    # Step 0 — admin rows
    _mark(desc.str.contains(_ADMIN_PATTERNS, na=False), 'Administrative/reference row')

    # Step 0a — merchandise
    not_yet = ~pd.Series(excluded, index=df.index)
    _mark(not_yet & desc.str.contains(_MERCH_PATTERNS, na=False), 'Merchandise giveaway')

    # Step 0b — standalone mug with no coffee signal
    not_yet = ~pd.Series(excluded, index=df.index)
    mug_hit = not_yet & desc.str.contains(r'\bMUG\b', na=False)
    no_sig  = ~desc.str.contains(_STRICT_COFFEE_SIGNAL, na=False)
    _mark(mug_hit & no_sig, 'Merchandise giveaway — standalone mug')

    # Step 1 — user global keywords
    if excl_global_kws:
        pat = re.compile('|'.join(re.escape(k) for k in excl_global_kws), re.IGNORECASE)
        not_yet = ~pd.Series(excluded, index=df.index)
        hit = desc[not_yet].str.contains(pat, na=False)
        for idx in hit[hit].index:
            loc = df.index.get_loc(idx)
            if not excluded[loc]:
                d = desc.at[idx]
                for kw, rsn in excl_global_kws.items():
                    if kw in d:
                        reason[loc] = rsn; break
                excluded[loc] = True

    # Step 2 — user HSN-specific keywords
    for hsn_str, kw_dict in excl_hsn_kws.items():
        hsn_mask = (hsn_s == hsn_str) & (~pd.Series(excluded, index=df.index))
        if not hsn_mask.any(): continue
        for kw, rsn in kw_dict.items():
            hit = desc[hsn_mask].str.contains(re.escape(kw), na=False)
            _mark(hit.reindex(df.index, fill_value=False), rsn)

    # Step 3 — strict coffee signal check for 21011190 / 21011200
    strict_mask = hsn_s.isin(STRICT_CHECK_HSNS) & (~pd.Series(excluded, index=df.index))
    if strict_mask.any():
        has_sig       = desc[strict_mask].str.contains(_STRICT_COFFEE_SIGNAL, na=False)
        no_sig_strict = strict_mask & (~has_sig.reindex(df.index, fill_value=False))
        _mark(no_sig_strict, 'No coffee signal — strict HSN check')

    # Step 4 — quantity-aware keyword exclusions
    not_yet = ~pd.Series(excluded, index=df.index)
    for kw, thr, rsn in QUANTITY_AWARE_EXCLUSIONS:
        if not not_yet.any(): break
        kw_hit   = not_yet & desc.str.contains(re.escape(kw), na=False)
        low_qty  = qty_mt < thr
        junk_hit = kw_hit & low_qty
        _mark(junk_hit, rsn)
        not_yet = not_yet & ~junk_hit

    return pd.Series(excluded, index=df.index), pd.Series(reason, index=df.index)


# ================================================================
# SECTION C — HSN NORMALISATION
# ================================================================

def norm_hsn_series(series):
    return (series.astype(str)
            .str.replace(r'\s+', '', regex=True)
            .str.split('.').str[0]
            .pipe(pd.to_numeric, errors='coerce')
            .fillna(0).astype(int))

def bucket_hsn_series(hsn_int):
    conds   = [hsn_int.isin(SOLUBLE_COFFEE_HSN), hsn_int.isin(CHICORY_PREMIX_HSN),
               hsn_int.isin(CHICORY_ONLY_HSN)]
    choices = ['SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY']
    return pd.Series(np.select(conds, choices, default='OTHER'), index=hsn_int.index)


# ================================================================
# SECTION D — CHICORY CLASSIFICATION
# ================================================================

KNOWN_BRANDS = [
    (r'NESCAFE.*SUNRISE|SUNRISE.*REGULAR|SUNRISE EXTRA|SUNRISE BLENDED|SUNRISE INSTA', 70, 30, 'CONFIRMED', 'Nestle Professional listing'),
    (r'NESCAFE CLASSIC',    100, 0,  'CONFIRMED', 'Pure instant coffee'),
    (r'NESCAFE GOLD',       100, 0,  'CONFIRMED', 'Premium pure coffee'),
    (r'NESCAFE INTENSO',    100, 0,  'CONFIRMED', 'Pure instant — confirmed'),
    (r'NESCAFE',            100, 0,  'ASSUMED',   'Generic Nescafe — assumed pure'),
    (r'BRU.*GOLD|BRU GOLD', 100, 0,  'CONFIRMED', 'Pure freeze dried'),
    (r'BRU.*GREEN LABEL|GREEN LABEL.*COFFEE', 80, 20, 'ASSUMED', 'Filter blend'),
    (r'BRU.*SELECT',        85, 15,  'ASSUMED',   'Premium blend'),
    (r'BRU INSTANT|BRU.*OPTIMA|BRU.*OPTM|BRU.*SUPER STRONG|BRU STRONG|BRU.*PLATINA|BRU.*EXPORT|BRU.*STAND UP|BRU.*AROMA|BRU.*INST', 70, 30, 'ASSUMED', 'Known chicory blend'),
    (r'TATA.*GRAND|TATA COFFEE GRAND', 70, 30, 'ASSUMED', 'Chicory mix indicated'),
    (r'TATA.*GOLD|TATA COFFEE GOLD',  100, 0,  'CONFIRMED', 'Pure coffee'),
    (r'TATA.*CLASSIC',      100, 0,  'ASSUMED',   'Usually pure'),
    (r'CONTINENTAL.*MALGUDI', 53, 47, 'CONFIRMED', 'Label states 53:47'),
    (r'CONTINENTAL.*XTRA|CONTINENTAL.*STRONG', 70, 30, 'ASSUMED', 'Tradeindia listing'),
    (r'CONTINENTAL.*SPECIAL|CONTINENTAL.*PURE', 100, 0, 'CONFIRMED', 'Pure variant'),
    (r'LEVISTA.*CLASSIC',   80, 20,  'ASSUMED',   'Chicory variant'),
    (r'LEVISTA.*80',        80, 20,  'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*70',        70, 30,  'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*60',        60, 40,  'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*PREMIUM|LEVISTA.*PURE', 100, 0, 'ASSUMED', 'Pure line'),
    (r'NARASUS.*UDHAYAM|NARASUS.*UDHAIYAM', 80, 20, 'ASSUMED', 'Blend positioning'),
    (r'NARASUS.*DELITE',    55, 45,  'ASSUMED',   'Label: 55:45'),
    (r'NARASUS.*BESH SUKKU|BESH SUKKU', 70, 30, 'ASSUMED', 'Sukku blend'),
    (r'NARASUS.*PURE|NARASUS PURE INSTANT|NARASUS INSTA STRONG|NARASUS STRONG INSTANT|NARASUS INSTANT', 100, 0, 'ASSUMED', 'Pure/instant line'),
    (r'SUNRISE COFFEE|SUNRISE.*BLENDED', 70, 30, 'CONFIRMED', 'Nestle Professional listing'),
    (r'COTHAS.*SPECIAL',    80, 20,  'ASSUMED',   'Special filter blend'),
    (r'COTHAS.*PREMIUM',    85, 15,  'ASSUMED',   'Premium blend'),
    (r'COTHAS.*80',         80, 20,  'ASSUMED',   'Ratio in name'),
    (r'KDC.*60|KDC.*70|KDC.*80', None, None, 'EXPLICIT_RATIO', 'Ratio in product name'),
]

def _extract_ratio(desc_up):
    m = re.search(r'\b(\d{2})\s*[:/]\s*(\d{2})\b', desc_up)
    if m: return int(m.group(1)), int(m.group(2))
    return None, None

def classify_chicory(desc_up):
    """
    Returns (category, coffee_pct, chicory_pct, confidence, notes) or None.
    category one of: 'EXPLICIT' | 'KNOWN_BRAND' | 'PURE_COFFEE' | 'ASSUMED'

    Sheet 2 ← EXPLICIT   (chicory word or numeric ratio found in the description text)
    Sheet 3 ← KNOWN_BRAND (matched to hard-coded brand reference table)
    Sheet 4 ← ASSUMED / PURE_COFFEE + any residual chicory signal rows
    """
    has_chicory = bool(re.search(r'CHICORY|CHICCORY|CICCORY|RICORY', desc_up))
    ratio_a, ratio_b = _extract_ratio(desc_up)

    if has_chicory and ratio_a is not None:
        return ('EXPLICIT', ratio_a, ratio_b, 'HIGH', 'Chicory word + ratio both in description')
    if has_chicory:
        return ('EXPLICIT', None, None, 'MEDIUM', 'Chicory stated in description — ratio not given')
    if ratio_a is not None:
        return ('EXPLICIT', ratio_a, ratio_b, 'MEDIUM', 'Numeric ratio in description — chicory implied')

    for pattern, c_pct, ch_pct, conf, notes in KNOWN_BRANDS:
        if re.search(pattern, desc_up):
            if conf == 'EXPLICIT_RATIO':
                r_a, r_b = _extract_ratio(desc_up)
                if r_a:
                    return ('EXPLICIT', r_a, r_b, 'HIGH', notes)
            if ch_pct == 0:
                return ('PURE_COFFEE', c_pct, ch_pct, conf, notes)
            return ('KNOWN_BRAND', c_pct, ch_pct, conf, notes)

    return None

# Broad pattern that catches chicory-risk rows not already in Sheet 2/3
CHICORY_SIGNAL_PAT = re.compile(
    r'CHICORY|CHICCORY|CICCORY|RICORY'
    r'|\b\d{2}\s*[:/]\s*\d{2}\b'
    r'|SUNRISE EXTRA|SUNRISE.*BLENDED|SUNRISE.*INSTA'
    r'|BRU INSTANT|BRU.*OPTIMA|BRU.*OPTM|BRU.*SUPER STRONG|BRU STRONG'
    r'|BRU.*PLATINA|BRU.*AROMA|BRU.*INST(?!.*GOLD)'
    r'|TATA.*GRAND|CONTINENTAL.*MALGUDI|CONTINENTAL.*XTRA|CONTINENTAL.*STRONG'
    r'|NARASUS.*UDHAYAM|NARASUS.*DELITE|NARASUS.*BESH SUKKU'
    r'|LEVISTA.*CLASSIC|LEVISTA.*[678]0',
    re.IGNORECASE,
)


# ================================================================
# SECTION E — MT CONVERSION (direct / parsed from description)
# ================================================================

_STOP_PAT_MT = re.compile(
    r'\b(?:OF|WITH|AND|FOR|NET|GROSS|EACH|PER|PACK|PKT|POUCH|BAG|BOX|CASE'
    r'|CARTON|SACHET|JAR|TIN|CAN|BOTTLE|UNIT|ASSORTED)\b'
)
PARSE_UNITS = {'NOS', 'PCS', 'CTM', 'CTN'}
DIRECT_KG   = {'KGS', 'KG'}
DIRECT_MT_U = {'MTS', 'MT'}
DIRECT_ML   = {'ML', 'MLT', 'LTR'}


def _convert_row_to_mt(row):
    """Row-level MT conversion for PARSE_UNITS rows. Returns (mt, status)."""
    qty  = row.get('STANDARD QUANTITY')
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()
    if pd.isna(qty):
        return np.nan, 'BLANK'
    try:
        qty = float(qty)
    except:
        return np.nan, 'BLANK'

    clean = _STOP_PAT_MT.sub(' ', desc).strip()
    clean = re.sub(r'\s+', ' ', clean)
    clean = clean.replace(' X ', 'X').replace(' x ', 'X').replace('*', 'X')

    # KG patterns
    for pat, fn in [
        (r'(\d+(?:\.\d+)?)\s*KGS?\s*X\s*(\d+)',  lambda m: float(m.group(1)) * float(m.group(2))),
        (r'(\d+(?:\.\d+)?)KGX(\d+)',               lambda m: float(m.group(1)) * float(m.group(2))),
        (r'(\d+)X(\d+(?:\.\d+)?)KG\b',             lambda m: float(m.group(1)) * float(m.group(2))),
        (r'(\d+(?:\.\d+)?)\s*KGS?\s*NET',          lambda m: float(m.group(1))),
    ]:
        m = re.search(pat, clean, re.IGNORECASE)
        if m: return qty * fn(m), 'PARSED'

    # Gram / ML patterns
    for pat, fn in [
        (r'(\d+(?:\.\d+)?)\s*GMS?\s*X\s*(\d+)\s*X\s*(\d+)', lambda m: float(m.group(1))*float(m.group(2))*float(m.group(3))/1e6),
        (r'(\d+(?:\.\d+)?)\s*G\s*X\s*(\d+)\s*X\s*(\d+)',     lambda m: float(m.group(1))*float(m.group(2))*float(m.group(3))/1e6),
        (r'(\d+)\((\d+)X(\d+(?:\.\d+)?)G\)',                  lambda m: float(m.group(1))*float(m.group(2))*float(m.group(3))/1e6),
        (r'\((\d+(?:\.\d+)?)\s*GMS?X(\d+)\)',                  lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'\((\d+)X(\d+(?:\.\d+)?)\s*GMS?\)',                  lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+(?:\.\d+)?)\s*GMS\s*X\s*(\d+)',                lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+(?:\.\d+)?)\s*GMX(\d+)',                        lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+(?:\.\d+)?)\s*GX(\d+)',                         lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+)X(\d+(?:\.\d+)?)\s*GMS\b',                    lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+)X(\d+(?:\.\d+)?)\s*GM\b',                     lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+)X(\d+(?:\.\d+)?)\s*G\b',                      lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+(?:\.\d+)?)\s*MLX(\d+)',                        lambda m: float(m.group(1))*float(m.group(2))/1e6),
        (r'(\d+)X(\d+(?:\.\d+)?)\s*ML\b',                     lambda m: float(m.group(1))*float(m.group(2))/1e6),
    ]:
        m = re.search(pat, clean, re.IGNORECASE)
        if m: return qty * fn(m), 'PARSED'

    for pat, div in [
        (r'(\d+(?:\.\d+)?)\s*GRAMS?\b', 1e6),
        (r'(\d+(?:\.\d+)?)\s*GRM\b',    1e6),
    ]:
        m = re.search(pat, clean, re.IGNORECASE)
        if m: return qty * float(m.group(1)) / div, 'PARSED'

    for suffix, div in [('GMS', 1e6), ('GM', 1e6), ('G', 1e6), ('KG', 1.0), ('ML', 1e6)]:
        vals = re.findall(r'(\d+(?:\.\d+)?)\s*' + suffix + r'\b', clean, re.IGNORECASE)
        if vals:
            val = float(vals[-1])
            if suffix == 'G' and val >= 5000: continue
            factor = val / div if suffix != 'KG' else val
            return qty * factor, 'PARSED'

    return np.nan, 'BLANK'


def convert_mt_vectorised(df):
    """Vectorised MT conversion. Returns (mt_series, status_series)."""
    qty  = pd.to_numeric(df.get('STANDARD QUANTITY', pd.Series(dtype=float)), errors='coerce')
    unit = df.get('STANDARD QUANTITY UNIT', pd.Series(dtype=str)).astype(str).str.upper().str.strip()

    is_blank = qty.isna()
    is_kgs   = unit.isin(DIRECT_KG)   & ~is_blank
    is_mt    = unit.isin(DIRECT_MT_U) & ~is_blank
    is_ml    = unit.isin(DIRECT_ML)   & ~is_blank
    is_parse = unit.isin(PARSE_UNITS) & ~is_blank

    mt_vals = pd.Series(np.nan, index=df.index)
    status  = pd.Series('BLANK', index=df.index)

    mt_vals[is_kgs] = qty[is_kgs] / 1000;      status[is_kgs] = 'DIRECT'
    mt_vals[is_mt]  = qty[is_mt];               status[is_mt]  = 'DIRECT'
    mt_vals[is_ml]  = qty[is_ml] / 1_000_000;  status[is_ml]  = 'DIRECT'

    if is_parse.any():
        parsed = df[is_parse].apply(_convert_row_to_mt, axis=1)
        mt_vals[is_parse] = parsed.apply(lambda x: x[0]).astype(float).values
        status[is_parse]  = parsed.apply(lambda x: x[1]).values

    return mt_vals, status


# ================================================================
# SECTION F — WATERFALL MT IMPUTATION TIERS
# (applied only to rows where MT is still blank/zero after Section E)
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
ICO_PRICES = {"SOLUBLE": 9500, "ROASTED": 6500, "GREEN": 4700, "DEFAULT": 5000}

IMP_CFG = {
    "suv_min_obs_high": 10,
    "suv_min_obs_low":  5,
    "max_plausible_mt": 30 * 28.28,
    "min_plausible_mt": 0.000001,
}

_UNIT_TO_G = {"KG": 1000.0, "KGS": 1000.0, "GM": 1.0, "GMS": 1.0, "G": 1.0}

_BULK_PATS = [
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

_BRAND_KWS_IMP = [
    "NESCAFE", "BOSCAFE", "SUNRISE", "DAVIDOFF", "NESCAFÉ", "BRU", "CONTINENTAL",
    "TATA COFFEE", "TATA", "MOCCONA", "DOUWE EGBERTS", "FOLGERS", "MAXWELL",
    "TCHIBO", "JACOBS", "LAVAZZA", "ILLY", "KOPIKO", "CAFE DESIRE", "CAFE VENDING",
    "AGGLOMERATED", "FREEZE DRIED", "SPRAY DRIED",
]
_STOP_PEER = {
    "COFFEE", "INSTANT", "SOLUBLE", "ROASTED", "GROUND", "EXPORT", "INDIA",
    "NOS", "PCS", "UNITS", "CARTONS", "KGS", "KG", "GMS", "GM", "NET", "GROSS",
}

# ── Column auto-detect ──────────────────────────────────────────
IMP_COL_CANDIDATES = {
    "col_mt":         ["MT", "MT_WEIGHT", "TOTAL_MT", "NET_WEIGHT_MT"],
    "col_mt_status":  ["MT_STATUS", "MT_CONVERSION_STATUS"],
    "col_fob":        ["FOB Value (USD)", "FOB_VALUE_USD", "FOB VALUE (USD)", "FOB VALUE", "FOB", "VALUE (USD)"],
    "col_unit":       ["STANDARD QUANTITY UNIT", "Unit", "UNIT", "UOM", "QTY UNIT"],
    "col_qty":        ["STANDARD QUANTITY", "Quantity", "QUANTITY", "QTY"],
    "col_desc":       ["PRODUCT DESCRIPTION", "Product Description", "DESCRIPTION"],
    "col_hs":         ["HS Code", "HS_CODE", "HSCODE", "HS CODE", "HSN CODE"],
    "col_port":       ["Port", "PORT", "PORT OF EXPORT", "ORIGIN PORT"],
    "col_exporter":   ["Exporter Name", "EXPORTER_NAME", "EXPORTER NAME", "EXPORTER", "SHIPPER"],
    "col_unit_price": ["Unit Price (USD)", "UNIT_PRICE_USD", "UNIT PRICE (USD)", "UNIT PRICE"],
    "col_date":       ["Shipment Date", "SHIPMENT_DATE", "SHIPMENT DATE", "DATE", "SB DATE"],
}

def _resolve_imp_cols(df):
    actual = {c.strip().lower(): c.strip() for c in df.columns}
    out = {}
    for key, candidates in IMP_COL_CANDIDATES.items():
        matched = None
        for c in candidates:
            if c.strip().lower() in actual:
                matched = actual[c.strip().lower()]; break
        if not matched:
            for c in candidates:
                cl = c.strip().lower()
                for al, ao in actual.items():
                    if cl in al or al in cl:
                        matched = ao; break
                if matched: break
        out[key] = matched
    return out


# ── T1: direct unit × factor ────────────────────────────────────
def _parse_unit_canonical(u):
    if pd.isna(u): return "UNKNOWN"
    u = str(u).strip().upper()
    if u in WEIGHT_UNIT_MAP: return u
    for key in PACKAGING_BENCHMARKS:
        if key in u: return key
    return u

def _bag_kg_from_price(up):
    if pd.isna(up) or up <= 0: return 60.0
    if 2.5 <= up / 60.0 <= 10.0: return 60.0
    for bkg in [50, 25, 10, 5, 1]:
        if 2.0 <= up / bkg <= 15.0: return float(bkg)
    return 60.0

def _tier1(row, cols, cfg):
    qc = cols.get("col_qty"); uc = cols.get("col_unit")
    fc = cols.get("col_fob"); pc = cols.get("col_unit_price")
    if not qc or not uc: return None
    qty = row.get(qc); unit_raw = str(row.get(uc, "")).strip().upper()
    if pd.isna(qty) or float(qty) <= 0: return None
    qty = float(qty)
    canonical = _parse_unit_canonical(unit_raw)
    if canonical in WEIGHT_UNIT_MAP:
        mt  = qty * WEIGHT_UNIT_MAP[canonical]
        fob = row.get(fc) if fc else None
        flag = "T1_UNIT_CONVERT" if (pd.notna(fob) and fob > 0) else "T1_UNIT_CONVERT_ZERO_FOB"
        return (mt, flag, mt * 0.95, mt * 1.05)
    if canonical in ("BAG", "SACK"):
        bkg = _bag_kg_from_price(row.get(pc) if pc else None)
        mt  = qty * bkg / 1000.0
        return (mt, "T1_UNIT_CONVERT", qty * 0.050, qty * 0.060)
    bm = {"BIG BAG": "FIBC", "SUPER": "JUMBO"}.get(canonical, canonical)
    if bm in PACKAGING_BENCHMARKS:
        c, lo, hi = PACKAGING_BENCHMARKS[bm]
        return (qty * c, "T1_UNIT_CONVERT", qty * lo, qty * hi)
    return None


# ── T1B: carton weight from description ─────────────────────────
def _to_g(val, unit_str):
    key = unit_str.upper().rstrip("S")
    return val * _UNIT_TO_G.get(key, _UNIT_TO_G.get(unit_str.upper(), 1.0))

def _extract_carton_kg(desc):
    if not desc or (isinstance(desc, float) and np.isnan(desc)): return None, None, None
    d = str(desc).upper().strip()
    if not d or any(p.search(d) for p in _BULK_PATS): return None, None, None
    _MIN, _MAX = 0.001, 50.0
    for regex, fn, label, conf in [
        (_P3,       lambda m: _to_g(float(m[-1][0]), m[-1][1]) / 1000.0,               "P3_NET_WT",  "HIGH"),
        (_P1_MULTI, lambda m: float(m[-1][0])*_to_g(float(m[-1][1]),m[-1][2])*float(m[-1][3])/1000.0, "P1_MULTI", "HIGH"),
        (_P1,       lambda m: float(m[-1][0])*_to_g(float(m[-1][1]),m[-1][2])/1000.0,  "P1_NxW",    "HIGH"),
        (_P2,       lambda m: _to_g(float(m[-1][0]),m[-1][1])*float(m[-1][2])/1000.0,  "P2_WxN",    "HIGH"),
        (_P4,       lambda m: _to_g(float(m[-1][0]),m[-1][1])*float(m[-1][2])/1000.0,  "P4_PAREN",  "MEDIUM"),
    ]:
        hits = regex.findall(d)
        if hits:
            try:
                kg = fn(hits)
                if _MIN <= kg <= _MAX: return kg, label, conf
            except: pass
    return None, None, None

def _tier1b(row, cols, cfg):
    qc = cols.get("col_qty"); dc = cols.get("col_desc")
    if not qc or not dc: return None
    qty = row.get(qc); desc = row.get(dc, "")
    if pd.isna(qty): return None
    qty = float(qty)
    kg, pattern, conf = _extract_carton_kg(desc)
    if kg is None: return None
    if qty == 0:
        mt = kg / 1000.0
        return (mt, f"T1B_DESC_{pattern}_ZERO_QTY", mt * 0.80, mt * 1.20)
    if qty <= 0: return None
    mt = qty * kg / 1000.0
    if mt < cfg["min_plausible_mt"] or mt > cfg["max_plausible_mt"]: return None
    lo, hi = (mt * 0.95, mt * 1.05) if conf == "HIGH" else (mt * 0.85, mt * 1.15)
    return (mt, f"T1B_DESC_{pattern}", lo, hi)


# ── T1C: named-brand peer lookup ────────────────────────────────
def _desc_tokens(desc):
    if not desc or (isinstance(desc, float) and np.isnan(desc)): return set()
    return {t for t in re.sub(r'[^A-Z0-9\s]', ' ', str(desc).upper()).split()
            if len(t) >= 3 and t not in _STOP_PEER}

def _jaccard(a, b):
    ta, tb = _desc_tokens(a), _desc_tokens(b)
    if not ta or not tb: return 0.0
    return len(ta & tb) / len(ta | tb)

def _build_peer_index(df, cols):
    cm = cols.get("col_mt");  cq = cols.get("col_qty")
    ce = cols.get("col_exporter"); cp = cols.get("col_port")
    ch = cols.get("col_hs");  cd = cols.get("col_desc")
    cdate = cols.get("col_date"); cu = cols.get("col_unit")
    if not all([cm, cq, ce, ch, cd]): return {}, {}
    base = df[df[cm].notna() & (df[cm] > 0) & df[cq].notna() & (df[cq] > 0)].copy()
    if base.empty or not cdate or cdate not in base.columns: return {}, {}
    base["_period"] = pd.to_datetime(base[cdate], errors="coerce").dt.to_period("M")
    base["_hs6"]    = base[ch].astype(str).str.replace(r'\D', '', regex=True).str[:6]
    base["_mpu"]    = base[cm] / base[cq]
    exp_idx = {}; port_idx = {}
    for _, r in base.iterrows():
        entry = (r["_period"], r[cd], r["_mpu"], r.get(cu, ""))
        exp_idx.setdefault((str(r[ce]).strip(), r["_hs6"]), []).append(entry)
        if cp: port_idx.setdefault((str(r.get(cp, "")).strip(), r["_hs6"]), []).append(entry)
    return exp_idx, port_idx

def _tier1c(row, exp_idx, port_idx, cols, cfg):
    dc = cols.get("col_desc"); qc = cols.get("col_qty")
    ec = cols.get("col_exporter"); pc = cols.get("col_port")
    hc = cols.get("col_hs");   datec = cols.get("col_date")
    desc = row.get(dc, "") if dc else ""
    if not any(b in str(desc).upper() for b in _BRAND_KWS_IMP): return None
    if not qc: return None
    qty = row.get(qc)
    if pd.isna(qty) or float(qty) <= 0: return None
    qty  = float(qty)
    hs6  = str(row.get(hc, "")).replace('.', '')[:6] if hc else ""
    exp  = str(row.get(ec, "")).strip()              if ec else ""
    port = str(row.get(pc, "")).strip()              if pc else ""
    try:
        tp = pd.Period(row[datec], "M") if (datec and datec in row and pd.notna(row.get(datec))) else None
    except: tp = None

    def _gap(p):
        try: return abs((p - tp).n) if tp and p else 999
        except: return 999

    is_bare = len(_desc_tokens(desc)) <= 2
    matched = [b for b in _BRAND_KWS_IMP if b in str(desc).upper()]
    best_score, best_mpu, best_src = -1, None, None

    for key, src in [((exp, hs6), "exporter"), ((port, hs6), "port")]:
        idx = exp_idx if src == "exporter" else port_idx
        candidates = idx.get(key, [])
        if is_bare:
            mpus = [mpu for per, pd_, mpu, _ in candidates
                    if _gap(per) <= 3 and any(b in str(pd_).upper() for b in matched) and mpu and mpu > 0]
            if mpus:
                med = float(np.median(mpus))
                if med > (best_mpu or 0):
                    best_score, best_mpu, best_src = 0.3, med, src + "_BARE"
        else:
            for per, pd_, mpu, _ in candidates:
                if _gap(per) > 3: continue
                sim = _jaccard(desc, pd_)
                if sim < 0.35: continue
                score = sim * max(0.4, 1.0 - _gap(per) * 0.15)
                if score > best_score:
                    best_score, best_mpu, best_src = score, mpu, src

    if not best_mpu or best_mpu <= 0: return None
    mt = qty * best_mpu
    if mt < cfg["min_plausible_mt"] or mt > cfg["max_plausible_mt"]: return None
    if "BARE" in str(best_src):
        lo, hi = mt * 0.60, mt * 1.40
        flag = f"T1C_PEER_{best_src.replace('_BARE','').upper()}_BARE_BRAND"
    else:
        margin = 0.15 if "exporter" in best_src else 0.25
        lo, hi = mt * (1 - margin), mt * (1 + margin)
        flag = f"T1C_PEER_{best_src.upper()}"
    return mt, flag, lo, hi


# ── T2: Standard Unit Value ──────────────────────────────────────
def _build_suv_table(df, cols, cfg):
    cm = cols.get("col_mt");   cf = cols.get("col_fob")
    ch = cols.get("col_hs");   cp = cols.get("col_port")
    cd = cols.get("col_date")
    if not all([cm, cf, ch, cp]): return {}
    base = df[df[cm].notna() & (df[cm] > 0) & df[cf].notna() & (df[cf] > 0)].copy()
    if base.empty: return {}
    base["_uv"]  = base[cf] / base[cm]
    base["_hs6"] = base[ch].astype(str).str.replace(r'\D', '', regex=True).str[:6]
    base["_per"] = (pd.to_datetime(base[cd], errors="coerce").dt.to_period("M").astype(str)
                    if cd and cd in base.columns else "ALL")
    suv = {}
    for (hs6, port, per), grp in base.groupby(["_hs6", cp, "_per"]):
        uv = grp["_uv"].dropna(); uv = uv[(uv > 0) & np.isfinite(uv)]
        n = len(uv)
        if n < cfg["suv_min_obs_low"]: continue
        med = float(np.median(uv)); std = float(np.std(uv)) if n > 1 else 0.0
        cv  = std / med if med > 0 else 999
        suv[(hs6, port, per)] = {"suv": med, "n": n}
    return suv

def _tier2(row, suv_table, cols, cfg):
    fc = cols.get("col_fob"); hc = cols.get("col_hs")
    pc = cols.get("col_port"); dc = cols.get("col_date")
    if not fc: return None
    fob = row.get(fc)
    if pd.isna(fob) or fob <= 0: return None
    hs6  = str(row.get(hc, "")).replace('.', '')[:6] if hc else ""
    port = str(row.get(pc, "")).strip()              if pc else ""
    try:
        per = pd.Period(row[dc], "M").strftime("%Y-%m") if (dc and pd.notna(row.get(dc))) else "ALL"
    except: per = "ALL"
    entry = suv_table.get((hs6, port, per))
    if entry is None:
        for (h, p, pp), e in suv_table.items():
            if h == hs6 and pp == per and e["n"] >= cfg["suv_min_obs_low"]:
                entry = e; break
    if entry is None: return None
    suv = entry["suv"]
    if suv <= 0: return None
    mt = fob / suv
    if mt < cfg["min_plausible_mt"] or mt > cfg["max_plausible_mt"]: return None
    sg = suv * 0.3
    return (mt, "T2_SUV_HS6", suv, entry["n"], fob / (suv + sg), fob / max(suv - sg, suv * 0.1))


# ── T3: temporal interpolation + ICO anchor ──────────────────────
def _detect_ico_group(hs_val):
    s = str(hs_val).replace('.', '').strip()
    if s[:4] == "2101":  return "SOLUBLE"
    if s[:5] == "09012": return "ROASTED"
    if s[:4] == "0901":  return "GREEN"
    return "DEFAULT"

def _build_temporal_index(df, cols):
    cm = cols.get("col_mt");  ce = cols.get("col_exporter")
    ch = cols.get("col_hs"); cd = cols.get("col_date")
    if not all([cm, ce, ch, cd]) or cd not in df.columns: return {}
    base = df[df[cm].notna() & (df[cm] > 0)].copy()
    base["_per"] = pd.to_datetime(base[cd], errors="coerce").dt.to_period("M")
    base["_hs4"] = base[ch].astype(str).str.replace(r'\D', '', regex=True).str[:4]
    t = {}
    for (exp, hs4), grp in base.groupby([ce, "_hs4"]):
        t[(str(exp).strip(), hs4)] = grp.groupby("_per")[cm].median().sort_index()
    return t

def _tier3(row, temporal_idx, cols, cfg):
    ce = cols.get("col_exporter"); ch = cols.get("col_hs")
    cf = cols.get("col_fob");      cd = cols.get("col_date")
    exp = str(row.get(ce, "")).strip() if ce else ""
    hs4 = str(row.get(ch, "")).replace('.', '')[:4] if ch else ""
    fob = row.get(cf) if cf else None
    # 3A — temporal
    if cd and cd in row and pd.notna(row.get(cd)):
        key = (exp, hs4)
        if key in temporal_idx:
            try:
                target = pd.Period(row[cd], "M")
                diffs  = [(abs((p - target).n), v) for p, v in temporal_idx[key].items()
                          if abs((p - target).n) <= 3]
                if diffs:
                    diffs.sort(); nd, nmt = diffs[0]
                    mt = nmt * max(0.5, 1.0 - nd * 0.1)
                    return (mt, "T3_INTERPOLATED", None, 0, mt * 0.7, mt * 1.3)
            except: pass
    # 3B — ICO anchor
    if fob is not None and pd.notna(fob) and fob > 0:
        group   = _detect_ico_group(row.get(ch, ""))
        ico_suv = ICO_PRICES.get(group, ICO_PRICES["DEFAULT"])
        mt      = fob / ico_suv
        if cfg["min_plausible_mt"] <= mt <= cfg["max_plausible_mt"]:
            return (mt, "T3_ICO_ANCHOR", ico_suv, 0, mt * 0.6, mt * 1.4)
    return (None, "IRRECOVERABLE", None, 0, None, None)


# ── Waterfall runner ─────────────────────────────────────────────
def run_imputation(df_in):
    """
    Apply waterfall imputation to blank/zero MT rows only.
    Rows that already have a valid MT value are left untouched (MT_FLAG = OBSERVED).
    Returns (df_out, counts_dict).
    """
    df   = df_in.copy()
    cols = _resolve_imp_cols(df)
    cfg  = IMP_CFG.copy()
    cm   = cols.get("col_mt")

    # Fallback column search
    if not cm or cm not in df.columns:
        for c in ["MT", "MT_WEIGHT", "TOTAL_MT"]:
            if c in df.columns:
                cm = c; cols["col_mt"] = c; break
    if not cm or cm not in df.columns:
        return df, {"error": "MT column not found"}

    cd = cols.get("col_date")
    if cd and cd in df.columns:
        df[cd] = pd.to_datetime(df[cd], errors="coerce")

    # Initialise output columns
    df["MT_FINAL"]       = np.nan
    df["MT_FLAG"]        = ""
    df["MT_SOURCE_TIER"] = -1
    df["MT_LOWER"]       = np.nan
    df["MT_UPPER"]       = np.nan

    # Mark rows that already have a valid MT value
    has_mt = df[cm].notna() & (df[cm] > 0)
    df.loc[has_mt, "MT_FINAL"]       = df.loc[has_mt, cm]
    df.loc[has_mt, "MT_FLAG"]        = "OBSERVED"
    df.loc[has_mt, "MT_SOURCE_TIER"] = 0

    # Build reference structures from observed rows only
    suv_table    = _build_suv_table(df, cols, cfg)
    exp_idx, port_idx = _build_peer_index(df, cols)
    temporal_idx = _build_temporal_index(df, cols)

    # Identify rows still needing imputation
    cs = cols.get("col_mt_status")
    blank_mask = df[cm].isna() | (df[cm] == 0)
    if cs and cs in df.columns:
        blank_mask = blank_mask | (df[cs].astype(str).str.strip().str.upper() == "BLANK")

    counts = {
        "OBSERVED": int(has_mt.sum()),
        "T1": 0, "T1B": 0, "T1C": 0, "T2": 0, "T3": 0, "IRRECOVERABLE": 0,
    }

    for idx, row in df[blank_mask].iterrows():
        result = _tier1(row, cols, cfg)
        if result:
            mt, flag, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt;  df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 1
            df.at[idx, "MT_LOWER"] = lo;  df.at[idx, "MT_UPPER"] = hi
            counts["T1"] += 1; continue

        result = _tier1b(row, cols, cfg)
        if result:
            mt, flag, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt;  df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 1
            df.at[idx, "MT_LOWER"] = lo;  df.at[idx, "MT_UPPER"] = hi
            counts["T1B"] += 1; continue

        result = _tier1c(row, exp_idx, port_idx, cols, cfg)
        if result:
            mt, flag, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt;  df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 1
            df.at[idx, "MT_LOWER"] = lo;  df.at[idx, "MT_UPPER"] = hi
            counts["T1C"] += 1; continue

        result = _tier2(row, suv_table, cols, cfg)
        if result:
            mt, flag, suv, n, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt;  df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 2
            df.at[idx, "MT_LOWER"] = lo;  df.at[idx, "MT_UPPER"] = hi
            counts["T2"] += 1; continue

        result = _tier3(row, temporal_idx, cols, cfg)
        mt, flag, suv, n, lo, hi = result
        if flag == "IRRECOVERABLE":
            df.at[idx, "MT_FLAG"] = "IRRECOVERABLE"
            df.at[idx, "MT_SOURCE_TIER"] = 3
            counts["IRRECOVERABLE"] += 1
        else:
            df.at[idx, "MT_FINAL"] = mt;  df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 3
            df.at[idx, "MT_LOWER"] = lo;  df.at[idx, "MT_UPPER"] = hi
            counts["T3"] += 1

    return df, counts


# ================================================================
# SECTION G — SINGLE EXCEL OUTPUT (4 sheets)
# ================================================================

SHEET_META = {
    "1 All Soluble Coffee":  ("0D3B66", "D6E4F0", "EBF4FA"),
    "2 Chicory Explicit":    ("1A5E20", "D4EDDA", "EAF7EC"),
    "3 Chicory Known Brand": ("7B4F00", "FFF3CD", "FFFAED"),
    "4 Chicory Assumed":     ("6A0572", "F3D6F5", "FAF0FB"),
}
# Columns to strip before writing to Excel
_INTERNAL_COLS = [
    '_HSN_INT', '_HSN_STR', '_DESC_UP', '_BUCKET',
    '_EXCLUDED', '_EXCL_REASON', '_CHICORY_CAT',
]

def _apply_sheet_format(wb, ws, df_out, sheet_name):
    hdr_hex, r1_hex, r2_hex = SHEET_META.get(sheet_name, ("0D3B66", "D6E4F0", "EBF4FA"))
    hdr  = wb.add_format({"bold": True, "bg_color": f"#{hdr_hex}", "font_color": "#FFFFFF",
                           "border": 1, "border_color": "#CCCCCC", "align": "center",
                           "valign": "vcenter", "text_wrap": True, "font_size": 10})
    row1 = wb.add_format({"bg_color": f"#{r1_hex}", "font_color": "#1A1A1A",
                           "border": 1, "border_color": "#CCCCCC", "font_size": 9})
    row2 = wb.add_format({"bg_color": f"#{r2_hex}", "font_color": "#1A1A1A",
                           "border": 1, "border_color": "#CCCCCC", "font_size": 9})
    for ci, cn in enumerate(df_out.columns):
        ws.write(0, ci, cn, hdr)
    for ri in range(1, len(df_out) + 1):
        ws.set_row(ri, None, row1 if ri % 2 == 1 else row2)
    for ci, cn in enumerate(df_out.columns):
        ws.set_column(ci, ci, min(max(len(str(cn)) + 4, 10), 44))
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(df_out), len(df_out.columns) - 1)

def build_output_excel(s1, s2, s3, s4):
    def _clean(df):
        return df.drop(columns=[c for c in _INTERNAL_COLS if c in df.columns],
                       errors='ignore').reset_index(drop=True)
    sheets = {
        "1 All Soluble Coffee":  _clean(s1),
        "2 Chicory Explicit":    _clean(s2),
        "3 Chicory Known Brand": _clean(s3),
        "4 Chicory Assumed":     _clean(s4),
    }
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        for name, df_out in sheets.items():
            df_out.to_excel(writer, sheet_name=name, index=False)
            _apply_sheet_format(writer.book, writer.sheets[name], df_out, name)
    buf.seek(0)
    return buf.getvalue()


# ================================================================
# SECTION H — MAIN PIPELINE FUNCTION
# ================================================================

def process_file(file, excl_df_json):
    """
    Runs the full pipeline on one uploaded file.
    Returns (sheet1, sheet2, sheet3, sheet4, counts) or None on error.

    Pipeline:
      1. Load & normalise HSN / description columns
      2. Apply exclusions → keep only valid soluble coffee rows (Sheet 1)
         This includes rescuing rows with correct soluble keywords filed under
         wrong HSN codes, so nothing is excluded purely on HSN mismatch.
      3. Direct MT conversion (Section E) — KGS/MT/NOS × parsed gram weight
      4. Waterfall imputation (Section F) — fills remaining blank MT rows only
      5. Chicory sub-classification → Sheet 2 / 3 / 4 as subsets of Sheet 1
    """
    # ── Load ──────────────────────────────────────────────────────
    try:    df = pd.read_excel(file, engine='calamine')
    except: df = pd.read_excel(file, engine='openpyxl')
    df.columns = df.columns.str.strip()

    # ── Detect columns ────────────────────────────────────────────
    hs_col = (next((c for c in df.columns if 'HS' in c.upper() and 'CODE' in c.upper()), None)
              or next((c for c in df.columns if 'HS' in c.upper()), None))
    desc_col = (next((c for c in df.columns if 'PRODUCT' in c.upper() and 'DESC' in c.upper()), None)
                or next((c for c in df.columns if 'DESC' in c.upper()), None))
    if not hs_col or not desc_col:
        st.error(f"Cannot find HS CODE or PRODUCT DESCRIPTION columns in **{file.name}**")
        return None

    # ── Helper columns ────────────────────────────────────────────
    df['_HSN_INT'] = norm_hsn_series(df[hs_col])
    df['_HSN_STR'] = df['_HSN_INT'].astype(str)
    df['_DESC_UP'] = df[desc_col].astype(str).str.upper().str.strip()
    df['_BUCKET']  = bucket_hsn_series(df['_HSN_INT'])

    # ── Exclusions ────────────────────────────────────────────────
    excl_global, excl_hsn = build_excl_list_lookup(excl_df_json)
    df['_EXCLUDED'], df['_EXCL_REASON'] = apply_exclusions(df, excl_global, excl_hsn)

    # ── Sheet 1: all valid soluble coffee rows ────────────────────
    # Include: correct target HSN rows (not excluded)
    #        + rows under any other HSN whose description contains a soluble keyword
    #          (these are wrong-HSN rescues — they ARE soluble coffee, just misfiled)
    correct_hsn      = df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX'])
    wrong_hsn_rescue = (
        ~df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY'])
        & df['_DESC_UP'].str.contains(sol_pattern, na=False, regex=True)
    )
    in_sheet1 = (correct_hsn | wrong_hsn_rescue) & ~df['_EXCLUDED']
    df_s1 = df[in_sheet1].copy()

    if df_s1.empty:
        st.warning(f"No soluble coffee rows found in **{file.name}** after filtering.")
        return None

    # ── MT conversion: direct / parsed ───────────────────────────
    # Standardise column names temporarily for convert_mt_vectorised
    sq_col  = (next((c for c in df_s1.columns if c.upper() == 'STANDARD QUANTITY'), None)
               or next((c for c in df_s1.columns if c.upper() in ['QUANTITY', 'QTY']), None))
    squ_col = (next((c for c in df_s1.columns if 'STANDARD' in c.upper() and 'UNIT' in c.upper()), None)
               or next((c for c in df_s1.columns if c.upper() in ['UNIT', 'UOM']), None))
    pd_col  = (next((c for c in df_s1.columns if 'PRODUCT' in c.upper() and 'DESC' in c.upper()), None)
               or next((c for c in df_s1.columns if 'DESC' in c.upper()), None))

    rename_map = {}
    if sq_col  and sq_col  != 'STANDARD QUANTITY':      rename_map[sq_col]  = 'STANDARD QUANTITY'
    if squ_col and squ_col != 'STANDARD QUANTITY UNIT': rename_map[squ_col] = 'STANDARD QUANTITY UNIT'
    if pd_col  and pd_col  != 'PRODUCT DESCRIPTION':    rename_map[pd_col]  = 'PRODUCT DESCRIPTION'

    if rename_map: df_s1 = df_s1.rename(columns=rename_map)
    df_s1['MT'], df_s1['MT_STATUS'] = convert_mt_vectorised(df_s1)
    if rename_map: df_s1 = df_s1.rename(columns={v: k for k, v in rename_map.items()})

    # ── Waterfall imputation on still-blank MT rows ───────────────
    df_s1, counts = run_imputation(df_s1)

    # ── Chicory sub-classification (Sheets 2, 3, 4) ──────────────
    clf_results = df_s1['_DESC_UP'].apply(classify_chicory)
    df_s1['_CHICORY_CAT'] = clf_results.apply(lambda x: x[0] if x else None)

    def _add_blend_cols(df_sub):
        idx = df_sub.index
        df_sub = df_sub.copy()
        df_sub['COFFEE_PCT']  = clf_results[idx].apply(lambda x: x[1] if x else None)
        df_sub['CHICORY_PCT'] = clf_results[idx].apply(lambda x: x[2] if x else None)
        df_sub['CONFIDENCE']  = clf_results[idx].apply(lambda x: x[3] if x else None)
        df_sub['BLEND_NOTES'] = clf_results[idx].apply(lambda x: x[4] if x else None)
        return df_sub

    # Sheet 2 — chicory EXPLICITLY named in description (word or ratio)
    df_s2 = _add_blend_cols(df_s1[df_s1['_CHICORY_CAT'] == 'EXPLICIT'].copy())

    # Sheet 3 — matched to known brand table
    df_s3 = _add_blend_cols(df_s1[df_s1['_CHICORY_CAT'] == 'KNOWN_BRAND'].copy())

    # Sheet 4 — assumed from brand name or any other description signal
    #   Includes: ASSUMED and PURE_COFFEE rows from brand table
    #           + any residual rows with a chicory signal not caught above
    s4_brand  = df_s1[df_s1['_CHICORY_CAT'].isin(['ASSUMED', 'PURE_COFFEE'])].copy()
    s4_signal = df_s1[
        df_s1['_CHICORY_CAT'].isna() &
        df_s1['_DESC_UP'].str.contains(CHICORY_SIGNAL_PAT, na=False)
    ].copy()
    df_s4 = _add_blend_cols(pd.concat([s4_brand, s4_signal], ignore_index=True))
    # Fill missing blend notes for signal-only rows
    df_s4['BLEND_NOTES'] = df_s4['BLEND_NOTES'].fillna('Chicory signal detected — no confirmed ratio')
    df_s4['CONFIDENCE']  = df_s4['CONFIDENCE'].fillna('LOW')

    return df_s1, df_s2, df_s3, df_s4, counts


# ================================================================
# SECTION I — UI
# ================================================================

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">LDC · Coffee Commercial · SIP 2026</div>
    <h1>Coffee Trade Intelligence</h1>
    <div class="hero-sub">UPLOAD → CLEAN → IMPUTE → DOWNLOAD</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stage-header">
    <span class="stage-num">STAGE 01</span>
    <span class="stage-title">Exclusion List</span>
</div>
""", unsafe_allow_html=True)
excl = st.file_uploader(
    "Upload exclusion list (.xlsx — must have a KEYWORD column)",
    type=["xlsx"], key="excl"
)

st.markdown("""
<div class="stage-header">
    <span class="stage-num">STAGE 02</span>
    <span class="stage-title">Raw CYBEX Files</span>
</div>
""", unsafe_allow_html=True)
raws = st.file_uploader(
    "Upload one or more raw CYBEX export files",
    type=["xlsx"], accept_multiple_files=True, key="raws"
)

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("▶  Run Pipeline", use_container_width=False)

if run_btn:
    if not excl:
        st.error("Please upload an exclusion list first.")
    elif not raws:
        st.error("Please upload at least one raw file.")
    else:
        excl_df = pd.read_excel(excl)
        excl_df.columns = excl_df.columns.str.strip().str.upper()
        if 'KEYWORD' not in excl_df.columns:
            st.error("Exclusion list must have a **KEYWORD** column.")
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

                with st.spinner("Cleaning, classifying, and imputing MT weights..."):
                    out = process_file(f, excl_df_json)

                if out is None:
                    continue

                s1, s2, s3, s4, counts = out
                total_rows = sum(v for k, v in counts.items() if k != "error")
                st.success(f"✓ Pipeline complete — {f.name}")

                # ── Sheet summary cards ─────────────────────────
                st.markdown(f"""
                <div class="sheet-summary">
                    <div class="sheet-card s1">
                        <div class="sheet-label">Sheet 1</div>
                        <div class="sheet-count">{len(s1):,}</div>
                        <div class="sheet-name">All Soluble Coffee<br>correct HSN + rescued rows</div>
                    </div>
                    <div class="sheet-card s2">
                        <div class="sheet-label">Sheet 2</div>
                        <div class="sheet-count">{len(s2):,}</div>
                        <div class="sheet-name">Chicory Explicit<br>keyword / ratio in description</div>
                    </div>
                    <div class="sheet-card s3">
                        <div class="sheet-label">Sheet 3</div>
                        <div class="sheet-count">{len(s3):,}</div>
                        <div class="sheet-name">Chicory Known Brand<br>matched to brand table</div>
                    </div>
                    <div class="sheet-card s4">
                        <div class="sheet-label">Sheet 4</div>
                        <div class="sheet-count">{len(s4):,}</div>
                        <div class="sheet-name">Chicory Assumed<br>brand name / signal detected</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Waterfall tier breakdown ────────────────────
                st.markdown("""
                <div class="stage-header" style="margin-top:28px">
                    <span class="stage-num">MT IMPUTATION</span>
                    <span class="stage-title">Waterfall Tier Breakdown — Sheet 1</span>
                </div>
                """, unsafe_allow_html=True)

                def pct(n):
                    return f"{n / total_rows * 100:.1f}%" if total_rows > 0 else "—"

                tier_info = [
                    ("OBSERVED",   counts.get("OBSERVED", 0),      "observed", "Ground Truth"),
                    ("TIER 1",     counts.get("T1", 0),            "tier1",    "Unit Convert"),
                    ("TIER 1B",    counts.get("T1B", 0),           "tier1b",   "Carton Pattern"),
                    ("TIER 1C",    counts.get("T1C", 0),           "tier1c",   "Brand Peer"),
                    ("TIER 2",     counts.get("T2", 0),            "tier2",    "SUV Estimate"),
                    ("TIER 3",     counts.get("T3", 0),            "tier3",    "ICO / Temporal"),
                    ("UNRESOLVED", counts.get("IRRECOVERABLE", 0), "irrecov",  "Irrecoverable"),
                ]

                cards = '<div class="tier-grid">'
                for label, n, cls, sub in tier_info:
                    cards += f"""<div class="tier-card {cls}">
                        <div class="tier-label">{label}</div>
                        <div class="tier-count">{n:,}</div>
                        <div class="tier-pct">{pct(n)} · {sub}</div>
                    </div>"""
                cards += '</div>'
                st.markdown(cards, unsafe_allow_html=True)

                # Stacked progress bar
                bar_colors = {
                    "OBSERVED": "#00d4aa", "T1": "#3b82f6", "T1B": "#8b5cf6",
                    "T1C": "#a78bfa", "T2": "#f59e0b", "T3": "#ef4444", "IRRECOVERABLE": "#374151",
                }
                bar = '<div class="tier-bar-wrap">'
                for key, color in bar_colors.items():
                    n = counts.get(key, 0)
                    w = n / total_rows * 100 if total_rows > 0 else 0
                    if w > 0:
                        bar += f'<div class="tier-bar-seg" style="width:{w:.2f}%;background:{color}"></div>'
                bar += '</div>'
                st.markdown(bar, unsafe_allow_html=True)

                # MT totals
                mc1, mc2, mc3 = st.columns(3)
                mt_obs = s1.loc[s1.get("MT_FLAG", pd.Series()) == "OBSERVED", "MT_FINAL"].sum() if "MT_FINAL" in s1 else 0
                mt_all = s1["MT_FINAL"].sum() if "MT_FINAL" in s1 else 0
                mt_imp = mt_all - mt_obs
                with mc1:
                    st.markdown(f"""<div class="result-box">
                        <div class="result-box-label">Observed MT</div>
                        <div class="result-mt">{mt_obs:,.1f}</div>
                        <div class="result-mt-sub">ground truth — untouched</div>
                    </div>""", unsafe_allow_html=True)
                with mc2:
                    st.markdown(f"""<div class="result-box">
                        <div class="result-box-label">Imputed MT</div>
                        <div class="result-mt">{mt_imp:,.1f}</div>
                        <div class="result-mt-sub">estimated by waterfall</div>
                    </div>""", unsafe_allow_html=True)
                with mc3:
                    st.markdown(f"""<div class="result-box">
                        <div class="result-box-label">Total MT</div>
                        <div class="result-mt">{mt_all:,.1f}</div>
                        <div class="result-mt-sub">Sheet 1 combined</div>
                    </div>""", unsafe_allow_html=True)

                # ── Single download button ──────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                with st.spinner("Building output file..."):
                    try:
                        out_bytes = build_output_excel(s1, s2, s3, s4)
                        st.download_button(
                            label=f"⬇  Download COFFEE_TRADE_{f.name}  (4 sheets)",
                            data=out_bytes,
                            file_name=f"COFFEE_TRADE_{f.name}",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{f.name}",
                        )
                    except Exception as e:
                        st.error(f"Excel generation failed: {e}")
