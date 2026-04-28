import streamlit as st
import pandas as pd
import numpy as np
import io
import re

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
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    border: 1px solid #1d4ed8;
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
# CONSTANTS — HSN BUCKETS
# ================================================================

SOLUBLE_COFFEE_HSN = {21011110, 21011120, 21011130, 21011190}
CHICORY_PREMIX_HSN = {21011200}
ALL_TARGET_HSN     = SOLUBLE_COFFEE_HSN | CHICORY_PREMIX_HSN
CHICORY_ONLY_HSN   = {21013010}
PURE_CHICORY_HSN   = {21013090, 21012020}
GROUND_COFFEE_HSN  = {9012190, 9019090, 9019020, 9011119, 9011129, 9012290}

# ================================================================
# CONSTANTS — KEYWORD PATTERNS
# ================================================================

# Soluble coffee detection — coffee-anchored to avoid false positives
# from freeze-dried herbs, ginger, dill, coriander etc.
SOLUBLE_KEYWORDS = [
    'INSTANT COFFEE',
    'SOLUBLE COFFEE',
    'SPRAY DRIED COFFEE',
    'FREEZE DRIED COFFEE',
    'AGGLOMERATED COFFEE',
    'AGGLOMERATED INSTANT',
    'FREEZE-DRIED COFFEE',
    'SPRAY-DRIED COFFEE',
    'COFFEE EXTRACT POWDER',
    'COFFEE PREMIX',
    'NESCAFE',
    'BRU INSTANT',
    'SUNRISE EXTRA',
]

CHICORY_WRONG_HSN_KEYWORDS = ['CHICORY', 'CHICCORY']

sol_pattern    = '|'.join(re.escape(k) for k in SOLUBLE_KEYWORDS)
chic_wrong_pat = '|'.join(re.escape(k) for k in CHICORY_WRONG_HSN_KEYWORDS)

# ================================================================
# ADMIN / REFERENCE ROW DETECTION  (structural — stays in code)
# These are purely administrative rows, never product shipments.
# Regex lookaheads needed here, so cannot live in a keyword list.
# ================================================================
_ADMIN_PATTERNS = re.compile(
    r'\b(?:GSTIN(?=\W)|GSTN(?=\W)|GST\s+NO(?=\W)'
    r'|TAX\s+INV(?:OICE)?|INV\s*NO|INVOICE\s*NO'
    r'|ICO\s+SI\s+NUMBER|ICO\s+MARK\s+NO|PERMIT\s+NUMBER'
    r'|REF\s*NO\.?:)',
    re.IGNORECASE,
)

# Merchandise giveaways — not coffee export volume
_MERCH_PATTERNS = re.compile(
    r'\b(?:TSHIRT|T-SHIRT|SAMPLING\s+TABLE|PROMOTIONAL\s+MATERIAL)',
    re.IGNORECASE,
)

# Strict coffee signal for HSN 21011190 / 21011200
_strict_coffee_signal_pattern = re.compile(
    r'COFFEE|CAPPUCCINO|CAPUCCINO|NESCAFE|BRU|LEVISTA|COTHAS|CONTINENTAL|NARASUS|TATA COFFEE|CHICORY|PREMIX',
    re.IGNORECASE
)
STRICT_CHECK_HSNS = {'21011190', '21011200'}

# ================================================================
# QUANTITY-AWARE EXCLUSIONS  (structural — stays in code)
# These need threshold logic that cannot live in a flat keyword list.
# Thresholds are in MT (0.05 MT = 50 KGS).
# ================================================================
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
# EXCLUSION LIST LOADER  (cached per unique file upload)
# ================================================================
@st.cache_data
def build_excl_list_lookup(excl_df_json):
    """
    Pre-process the user exclusion list into two lookup structures.
    Accepts JSON string so st.cache_data can hash it.
    Uses vectorised pandas — no iterrows().
    """
    excl_df = pd.read_json(io.StringIO(excl_df_json))
    global_kws = {}
    hsn_kws    = {}

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


# ================================================================
# VECTORISED EXCLUSION
# Step order:
#   0  — Admin/reference rows (regex — structural)
#   0a — Merchandise giveaways (regex — structural)
#   0b — MUG coffee-aware check (structural)
#   1  — User exclusion list global keywords
#   2  — User exclusion list HSN-specific keywords
#   3  — Strict coffee signal check for 21011190 / 21011200
#   4  — Quantity-aware keyword exclusions (structural)
# ================================================================
def apply_exclusions_vectorised(df, excl_global_kws, excl_hsn_kws):
    desc  = df['_DESC_UP']
    hsn_s = df['_HSN_INT'].astype(str)

    # Convert quantity to MT for quantity-aware checks
    qty_col_candidates  = ['STANDARD QUANTITY', 'QUANTITY', 'QTY', 'STD QTY']
    unit_col_candidates = ['UNIT', 'STANDARD QUANTITY UNIT', 'UOM', 'QTY UNIT']
    qty_col  = next((c for c in qty_col_candidates  if c in df.columns), None)
    unit_col = next((c for c in unit_col_candidates if c in df.columns), None)

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

    # ── 0. Admin / reference rows ──
    hit = desc.str.contains(_ADMIN_PATTERNS, na=False)
    excluded |= hit.values
    reason[hit.values & (reason == '')] = 'Administrative/reference row — not a product line'

    # ── 0a. Merchandise giveaways ──
    merch_hit = (~pd.Series(excluded, index=df.index)) & desc.str.contains(_MERCH_PATTERNS, na=False)
    pos = df.index.get_indexer(merch_hit[merch_hit].index)
    excluded[pos] = True
    for p in pos:
        if reason[p] == '':
            reason[p] = 'Merchandise giveaway — not coffee export volume'

    # ── 0b. MUG — coffee-aware check ──
    not_yet = ~pd.Series(excluded, index=df.index)
    mug_hit = not_yet & desc.str.contains(r'\bMUG\b', na=False)
    no_coffee_signal = ~desc.str.contains(_strict_coffee_signal_pattern, na=False)
    mug_junk = mug_hit & no_coffee_signal
    pos = df.index.get_indexer(mug_junk[mug_junk].index)
    excluded[pos] = True
    for p in pos:
        if reason[p] == '':
            reason[p] = 'Merchandise giveaway — standalone mug'

    # ── 1. User exclusion list — global keywords ──
    if excl_global_kws:
        user_global_pat = re.compile(
            '|'.join(re.escape(k) for k in excl_global_kws),
            re.IGNORECASE
        )
        mask = ~pd.Series(excluded, index=df.index)
        if mask.any():
            hit = desc[mask].str.contains(user_global_pat, na=False)
            for idx in hit[hit].index:
                loc = df.index.get_loc(idx)
                if not excluded[loc]:
                    d = desc.at[idx]
                    for kw, rsn in excl_global_kws.items():
                        if kw in d:
                            reason[loc] = rsn
                            break
                    excluded[loc] = True

    # ── 2. User exclusion list — HSN-specific keywords ──
    for hsn_str, kw_dict in excl_hsn_kws.items():
        hsn_mask = (hsn_s == hsn_str) & (~pd.Series(excluded, index=df.index))
        if not hsn_mask.any():
            continue
        for kw, rsn in kw_dict.items():
            hit = desc[hsn_mask].str.contains(re.escape(kw), na=False, regex=True)
            idx = hit[hit].index
            pos = df.index.get_indexer(idx)
            excluded[pos] = True
            for p in pos:
                if reason[p] == '':
                    reason[p] = rsn

    # ── 3. Strict coffee signal check for 21011190 / 21011200 ──
    strict_mask = hsn_s.isin(STRICT_CHECK_HSNS) & (~pd.Series(excluded, index=df.index))
    if strict_mask.any():
        has_signal = desc[strict_mask].str.contains(_strict_coffee_signal_pattern, na=False)
        no_signal  = strict_mask & (~has_signal.reindex(df.index, fill_value=False))
        pos = df.index.get_indexer(no_signal[no_signal].index)
        excluded[pos] = True
        for p in pos:
            if reason[p] == '':
                reason[p] = 'No coffee signal — strict check for HSN'

    # ── 4. Quantity-aware keyword exclusions ──
    not_yet_excluded = ~pd.Series(excluded, index=df.index)
    for kw, qty_threshold, junk_reason in QUANTITY_AWARE_EXCLUSIONS:
        if not not_yet_excluded.any():
            break
        kw_hit  = not_yet_excluded & desc.str.contains(re.escape(kw), na=False)
        low_qty = qty_mt < qty_threshold
        junk_hit = kw_hit & low_qty
        pos = df.index.get_indexer(junk_hit[junk_hit].index)
        excluded[pos] = True
        for p in pos:
            if reason[p] == '':
                reason[p] = junk_reason
        not_yet_excluded = not_yet_excluded & ~junk_hit

    return pd.Series(excluded, index=df.index), pd.Series(reason, index=df.index)


# ================================================================
# HSN BUCKETING — vectorised
# ================================================================
def norm_hsn_series(series):
    return (
        series.astype(str)
              .str.replace(r'\s+', '', regex=True)
              .str.split('.').str[0]
              .pipe(pd.to_numeric, errors='coerce')
              .fillna(0)
              .astype(int)
    )

def bucket_hsn_series(hsn_series):
    conditions = [
        hsn_series.isin(SOLUBLE_COFFEE_HSN),
        hsn_series.isin(CHICORY_PREMIX_HSN),
        hsn_series.isin(CHICORY_ONLY_HSN),
        hsn_series.isin(PURE_CHICORY_HSN),
        hsn_series.isin(GROUND_COFFEE_HSN),
    ]
    choices = ['SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY', 'PURE_CHICORY', 'GROUND_COFFEE']
    return pd.Series(np.select(conditions, choices, default='OTHER'), index=hsn_series.index)

def norm_hsn(v):
    try:
        return int(str(v).replace(' ', '').strip().split('.')[0])
    except:
        return 0


# ================================================================
# WRONG HSN SCANNER
# ================================================================
def find_wrong_hsn_rows(df, hs_col):
    scannable_mask = (
        ~df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY', 'PURE_CHICORY'])
    )
    df_scan = df[scannable_mask].copy()

    df_scan['_WRONG_SOLUBLE'] = df_scan['_DESC_UP'].str.contains(
        sol_pattern, na=False, regex=True
    )
    df_scan['_WRONG_CHICORY'] = df_scan['_DESC_UP'].str.contains(
        chic_wrong_pat, na=False, regex=True
    )
    df_scan['_WRONG_ANY'] = df_scan['_WRONG_SOLUBLE'] | df_scan['_WRONG_CHICORY']

    return df_scan[df_scan['_WRONG_ANY']].copy()


# ================================================================
# KNOWN BRAND CHICORY CLASSIFICATION TABLE
# ================================================================
KNOWN_BRANDS = [
    (r'NESCAFE.*SUNRISE|SUNRISE.*REGULAR|SUNRISE EXTRA|SUNRISE BLENDED|SUNRISE INSTA', 70, 30, 'CONFIRMED', 'Nestle Professional listing'),
    (r'NESCAFE CLASSIC',   100, 0,  'CONFIRMED', 'Pure instant coffee'),
    (r'NESCAFE GOLD',      100, 0,  'CONFIRMED', 'Premium pure coffee'),
    (r'NESCAFE INTENSO',   100, 0,  'CONFIRMED', 'Pure instant — confirmed'),
    (r'NESCAFE',           100, 0,  'ASSUMED',   'Generic Nescafe — assumed pure unless variant known'),
    (r'BRU.*GOLD|BRU GOLD',100, 0,  'CONFIRMED', 'Pure freeze dried'),
    (r'BRU.*GREEN LABEL|GREEN LABEL.*COFFEE', 80, 20, 'ASSUMED', 'Filter blend'),
    (r'BRU.*SELECT',        85, 15, 'ASSUMED',   'Premium blend'),
    (r'BRU INSTANT|BRU.*OPTIMA|BRU.*OPTM|BRU.*SUPER STRONG|BRU STRONG|BRU.*PLATINA|BRU.*EXPORT|BRU.*STAND UP|BRU.*AROMA|BRU.*INST', 70, 30, 'ASSUMED', 'Known chicory blend'),
    (r'TATA.*GRAND|TATA COFFEE GRAND', 70, 30, 'ASSUMED', 'Chicory mix indicated'),
    (r'TATA.*GOLD|TATA COFFEE GOLD',  100, 0,  'CONFIRMED', 'Pure coffee'),
    (r'TATA.*CLASSIC',     100, 0,  'ASSUMED',   'Usually pure'),
    (r'CONTINENTAL.*MALGUDI', 53, 47, 'CONFIRMED', 'Label states 53:47'),
    (r'CONTINENTAL.*XTRA|CONTINENTAL.*STRONG', 70, 30, 'ASSUMED', 'Tradeindia listing'),
    (r'CONTINENTAL.*SPECIAL|CONTINENTAL.*PURE', 100, 0, 'CONFIRMED', 'Pure variant'),
    (r'LEVISTA.*CLASSIC',   80, 20, 'ASSUMED',   'Chicory variant'),
    (r'LEVISTA.*80',        80, 20, 'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*70',        70, 30, 'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*60',        60, 40, 'ASSUMED',   'Blend ratio in name'),
    (r'LEVISTA.*PREMIUM|LEVISTA.*PURE', 100, 0, 'ASSUMED', 'Pure line'),
    (r'NARASUS.*UDHAYAM|NARASUS.*UDHAIYAM', 80, 20, 'ASSUMED', 'Blend positioning'),
    (r'NARASUS.*DELITE',    55, 45, 'ASSUMED',   'Label: 55:45'),
    (r'NARASUS.*BESH SUKKU|BESH SUKKU', 70, 30, 'ASSUMED', 'Sukku blend'),
    (r'NARASUS.*PURE|NARASUS PURE INSTANT|NARASUS INSTA STRONG|NARASUS STRONG INSTANT|NARASUS INSTANT', 100, 0, 'ASSUMED', 'Pure/instant line'),
    (r'SUNRISE COFFEE|SUNRISE.*BLENDED', 70, 30, 'CONFIRMED', 'Nestle Professional listing'),
    (r'COTHAS.*SPECIAL',    80, 20, 'ASSUMED',   'Special filter blend'),
    (r'COTHAS.*PREMIUM',    85, 15, 'ASSUMED',   'Premium blend'),
    (r'COTHAS.*80',         80, 20, 'ASSUMED',   'Ratio in name'),
    (r'KDC.*60|KDC.*70|KDC.*80', None, None, 'EXPLICIT_RATIO', 'Ratio in product name — use extract_ratio'),
]

def extract_ratio(desc_up):
    m = re.search(r'\b(\d{2})\s*[:/]\s*(\d{2})\b', desc_up)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None

def classify_chicory_row(desc_up):
    has_chicory_word = bool(re.search(r'CHICORY|CHICCORY|CICCORY|RICORY', desc_up))
    ratio_a, ratio_b = extract_ratio(desc_up)

    if has_chicory_word and ratio_a is not None:
        return ('EXPLICIT', ratio_a, ratio_b, 'HIGH', 'Chicory + ratio both stated in description')
    if has_chicory_word:
        return ('EXPLICIT', None, None, 'MEDIUM', 'Chicory stated, ratio not given')
    if ratio_a is not None:
        return ('EXPLICIT', ratio_a, ratio_b, 'MEDIUM', 'Ratio in description, chicory not named')

    for pattern, c_pct, ch_pct, conf, notes in KNOWN_BRANDS:
        if re.search(pattern, desc_up):
            if conf == 'EXPLICIT_RATIO':
                r_a, r_b = extract_ratio(desc_up)
                if r_a:
                    return ('EXPLICIT', r_a, r_b, 'HIGH', notes)
            if ch_pct == 0:
                return ('PURE_COFFEE', c_pct, ch_pct, conf, notes)
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
# MT CONVERSION
# ================================================================
STOP_WORDS = ['OF', 'WITH', 'AND', 'FOR', 'NET', 'GROSS', 'EACH',
              'PER', 'PACK', 'PKT', 'POUCH', 'BAG', 'BOX', 'CASE', 'CARTON',
              'SACHET', 'JAR', 'TIN', 'CAN', 'BOTTLE', 'UNIT', 'ASSORTED']

_STOP_PAT = re.compile(
    r'\b(' + '|'.join(re.escape(w) for w in STOP_WORDS) + r')\b'
)

PARSE_UNITS = {'NOS', 'PCS', 'CTM', 'CTN'}
DIRECT_KG   = {'KGS', 'KG'}
DIRECT_MT   = {'MTS', 'MT'}
DIRECT_ML   = {'ML', 'MLT', 'LTR'}

def convert_to_mt(row):
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper().strip()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()

    if pd.isna(qty):
        return np.nan, 'BLANK'
    try:
        qty = float(qty)
    except (ValueError, TypeError):
        return np.nan, 'BLANK'

    if unit in DIRECT_KG:
        return qty / 1000, 'DIRECT'
    if unit in DIRECT_MT:
        return qty, 'DIRECT'
    if unit in DIRECT_ML:
        return qty / 1_000_000, 'DIRECT'

    if unit in PARSE_UNITS:
        try:
            clean = _STOP_PAT.sub(' ', desc).strip()
            clean = re.sub(r'\s+', ' ', clean)
            clean = clean.replace(' X ', 'X').replace(' x ', 'X').replace('*', 'X')

            m = re.search(r'(\d+(?:\.\d+)?)\s*KGS?\s*X\s*(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)), 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)KGX(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)), 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)KG\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)), 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*KGS?\s*NET', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)), 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GMS?\s*X\s*(\d+)\s*X\s*(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) * float(m.group(3)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*G\s*X\s*(\d+)\s*X\s*(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) * float(m.group(3)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)\((\d+)X(\d+(?:\.\d+)?)G\)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) * float(m.group(3)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)\D+X\s*(\d+)\D+X\s*(\d+(?:\.\d+)?)\s*GMS?\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) * float(m.group(3)) / 1_000_000, 'PARSED'

            m = re.search(r'\((\d+(?:\.\d+)?)\s*GMS?X(\d+)\)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'\((\d+)X(\d+(?:\.\d+)?)\s*GMS?\)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GMS\s*X\s*(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GMX(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GX(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)\s*GMS\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)\s*GM\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)\s*G\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*MLX(\d+)', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)\s*ML\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GRAMS?\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GRM\b', clean, re.IGNORECASE)
            if m:
                return qty * float(m.group(1)) / 1_000_000, 'PARSED'

            gms = re.findall(r'(\d+(?:\.\d+)?)\s*GMS\b', clean, re.IGNORECASE)
            if gms:
                return qty * float(gms[-1]) / 1_000_000, 'PARSED'

            gm = re.findall(r'(\d+(?:\.\d+)?)\s*GM\b', clean, re.IGNORECASE)
            if gm:
                return qty * float(gm[-1]) / 1_000_000, 'PARSED'

            g = re.findall(r'(\d+(?:\.\d+)?)\s*G\b', clean, re.IGNORECASE)
            if g:
                val = float(g[-1])
                if val < 5000:
                    return qty * val / 1_000_000, 'PARSED'

            kg = re.findall(r'(\d+(?:\.\d+)?)\s*KG\b', clean, re.IGNORECASE)
            if kg:
                return qty * float(kg[-1]), 'PARSED'

            ml = re.findall(r'(\d+(?:\.\d+)?)\s*ML\b', clean, re.IGNORECASE)
            if ml:
                return qty * float(ml[-1]) / 1_000_000, 'PARSED'

        except Exception:
            return np.nan, 'BLANK'

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

    mt_vals[is_kgs] = qty[is_kgs] / 1000
    status[is_kgs]  = 'DIRECT'
    mt_vals[is_mt]  = qty[is_mt]
    status[is_mt]   = 'DIRECT'
    mt_vals[is_ml]  = qty[is_ml] / 1_000_000
    status[is_ml]   = 'DIRECT'

    if is_parse.any():
        parsed_results = df[is_parse].apply(convert_to_mt, axis=1)
        mt_vals[is_parse] = parsed_results.apply(lambda x: x[0]).astype(float).values
        status[is_parse]  = parsed_results.apply(lambda x: x[1]).values

    return mt_vals, status


# ================================================================
# EXCEL FORMATTING
# ================================================================
EXCEL_SHEETS = [
    '1 All Soluble Coffee',
    '2 Chicory Explicit Ratio',
    '3 Chicory Known Brand',
    '4 Chicory Assumed',
    '5 Chicory Only Exports',
    'Summary',
]

SHEET_COLOURS = {
    '1 All Soluble Coffee':      ('1F4E79', 'D6E4F0', 'EBF4FA'),
    '2 Chicory Explicit Ratio':  ('1A5E20', 'D4EDDA', 'EAF7EC'),
    '3 Chicory Known Brand':     ('7B4F00', 'FFF3CD', 'FFFAED'),
    '4 Chicory Assumed':         ('6A0572', 'F3D6F5', 'FAF0FB'),
    '5 Chicory Only Exports':    ('2C3E50', 'D5DBDB', 'F2F3F4'),
    'Summary':                   ('0D3B66', 'D6E4F0', 'EBF4FA'),
}

def _hex(h):
    return f'#{h}'

def write_excel(sheets_dict):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        for sheet_name in EXCEL_SHEETS:
            if sheet_name not in sheets_dict:
                continue
            df_out = sheets_dict[sheet_name]
            df_out.to_excel(writer, sheet_name=sheet_name, index=False)

            wb  = writer.book
            ws  = writer.sheets[sheet_name]
            colours = SHEET_COLOURS.get(sheet_name, ('1F4E79', 'D6E4F0', 'EBF4FA'))
            hdr_hex, row1_hex, row2_hex = colours

            hdr_fmt = wb.add_format({
                'bold': True, 'bg_color': _hex(hdr_hex), 'font_color': '#FFFFFF',
                'border': 1, 'border_color': '#CCCCCC',
                'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                'font_size': 10,
            })
            row1_fmt = wb.add_format({
                'bg_color': _hex(row1_hex), 'font_color': '#1A1A1A',
                'border': 1, 'border_color': '#CCCCCC', 'font_size': 9,
            })
            row2_fmt = wb.add_format({
                'bg_color': _hex(row2_hex), 'font_color': '#1A1A1A',
                'border': 1, 'border_color': '#CCCCCC', 'font_size': 9,
            })

            for col_idx, col_name in enumerate(df_out.columns):
                ws.write(0, col_idx, col_name, hdr_fmt)

            for row_idx in range(1, len(df_out) + 1):
                fmt = row1_fmt if row_idx % 2 == 1 else row2_fmt
                ws.set_row(row_idx, None, fmt)

            for col_idx, col_name in enumerate(df_out.columns):
                width = min(max(len(str(col_name)) + 4, 10), 40)
                ws.set_column(col_idx, col_idx, width)

            ws.freeze_panes(1, 0)

    buf.seek(0)
    return buf.getvalue()


# ================================================================
# MAIN PROCESSING FUNCTION
# ================================================================
DROP_COLS = ['_HSN_INT', '_DESC_UP', '_BUCKET', '_EXCLUDED', '_EXCL_REASON',
             '_IS_CHICORY_SIGNAL', '_WRONG_SOLUBLE', '_WRONG_CHICORY', '_WRONG_ANY',
             '_SOURCE_TEMP']

def clean_export(df_in):
    keep = [c for c in df_in.columns if c not in DROP_COLS]
    return df_in[keep].reset_index(drop=True)

def process_file(file, excl_df_json):
    try:
        df = pd.read_excel(file, engine='calamine')
    except Exception:
        df = pd.read_excel(file, engine='openpyxl')
    df.columns = df.columns.str.strip()

    hs_col = next((c for c in df.columns if 'HS' in c.upper() and 'CODE' in c.upper()), None)
    if not hs_col:
        hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)
    desc_col = next((c for c in df.columns if 'PRODUCT' in c.upper() and 'DESC' in c.upper()), None)
    if not desc_col:
        desc_col = next((c for c in df.columns if 'DESC' in c.upper()), None)

    if not hs_col or not desc_col:
        st.error(f"Could not find HS CODE or PRODUCT DESCRIPTION columns in {file.name}")
        return None

    df['_HSN_INT'] = norm_hsn_series(df[hs_col])
    df['_DESC_UP'] = df[desc_col].astype(str).str.upper().str.strip()
    df['_BUCKET']  = bucket_hsn_series(df['_HSN_INT'])

    excl_global_kws, excl_hsn_kws = build_excl_list_lookup(excl_df_json)
    df['_EXCLUDED'], df['_EXCL_REASON'] = apply_exclusions_vectorised(
        df, excl_global_kws, excl_hsn_kws
    )

    df_wrong = find_wrong_hsn_rows(df, hs_col)
    df_wrong = df_wrong[~df_wrong['_EXCLUDED']].copy()
    df_wrong['_SOURCE'] = 'Wrong HSN — flagged'

    df_correct = df[
        df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX']) & ~df['_EXCLUDED']
    ].copy()
    df_correct['_SOURCE'] = 'Correct HSN'

    df_sheet1 = pd.concat([df_correct, df_wrong], ignore_index=True)

    df_sheet1['MT'], df_sheet1['MT_STATUS'] = convert_to_mt_vectorised(df_sheet1)

    df_sheet1['_IS_CHICORY_SIGNAL'] = df_sheet1['_DESC_UP'].str.contains(
        CHICORY_SIGNAL_PATTERN, na=False, regex=True
    )

    df_chicory_pool = df_sheet1[df_sheet1['_IS_CHICORY_SIGNAL']].copy()

    def apply_classification(df_in):
        results = df_in['_DESC_UP'].apply(classify_chicory_row)
        df_in = df_in.copy()
        df_in['BLEND_CATEGORY'] = results.apply(lambda x: x[0] if x else 'ASSUMED')
        df_in['COFFEE_PCT']     = results.apply(lambda x: x[1] if x else None)
        df_in['CHICORY_PCT']    = results.apply(lambda x: x[2] if x else None)
        df_in['CONFIDENCE']     = results.apply(lambda x: x[3] if x else 'LOW')
        df_in['BLEND_NOTES']    = results.apply(lambda x: x[4] if x else 'Chicory signal but no confirmed ratio')
        return df_in

    df_chicory_pool = apply_classification(df_chicory_pool)

    df_premix = df_sheet1[
        (df_sheet1['_BUCKET'] == 'CHICORY_PREMIX') &
        (~df_sheet1.index.isin(df_chicory_pool.index))
    ].copy()
    df_premix = apply_classification(df_premix)

    df_all_chicory = pd.concat([df_chicory_pool, df_premix], ignore_index=True)

    df_chic_explicit = df_all_chicory[df_all_chicory['BLEND_CATEGORY'] == 'EXPLICIT'].copy()
    df_chic_known    = df_all_chicory[df_all_chicory['BLEND_CATEGORY'] == 'KNOWN_BRAND'].copy()
    df_chic_assumed  = df_all_chicory[df_all_chicory['BLEND_CATEGORY'].isin(['ASSUMED', 'PURE_COFFEE'])].copy()

    df_chicory_only = df[df['_BUCKET'] == 'CHICORY_ONLY'].copy()
    if len(df_chicory_only):
        df_chicory_only['MT'], df_chicory_only['MT_STATUS'] = convert_to_mt_vectorised(df_chicory_only)

    df_excl_from_target = df[
        df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX']) & df['_EXCLUDED']
    ].copy()
    df_excl_from_target['_EXCL_SOURCE'] = 'Keyword exclusion — target HSN'

    scannable_mask = ~df['_BUCKET'].isin([
        'SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY', 'PURE_CHICORY'
    ])
    df_other_not_flagged = df[scannable_mask].copy()
    df_other_not_flagged = df_other_not_flagged[
        ~df_other_not_flagged.index.isin(df_wrong.index)
    ].copy()
    df_other_not_flagged['_EXCL_SOURCE'] = 'Other HSN — not flagged as soluble'

    df_excluded_review = pd.concat(
        [df_excl_from_target, df_other_not_flagged], ignore_index=True
    )

    summary_df = pd.DataFrame([
        {'Sheet': '1 All Soluble Coffee',     'Rows': len(df_sheet1),          'Notes': 'Correct HSN + wrong HSN rescued rows'},
        {'Sheet': '2 Chicory Explicit Ratio', 'Rows': len(df_chic_explicit),   'Notes': 'Ratio or chicory word in product description'},
        {'Sheet': '3 Chicory Known Brand',    'Rows': len(df_chic_known),      'Notes': 'Matched to brand reference table'},
        {'Sheet': '4 Chicory Assumed',        'Rows': len(df_chic_assumed),    'Notes': 'Chicory signal but no confirmed ratio'},
        {'Sheet': '5 Chicory Only Exports',   'Rows': len(df_chicory_only),    'Notes': 'HSN 21013010 — pure roasted chicory exports'},
        {'Sheet': '6 Excluded Items Review',  'Rows': len(df_excluded_review), 'Notes': 'Non-soluble products removed'},
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
# UI
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
        excl_df.columns = excl_df.columns.str.strip().str.upper()
        if 'KEYWORD' not in excl_df.columns:
            st.error("Exclusion list must have a KEYWORD column")
        else:
            excl_df_json = excl_df.to_json()
            for f in raws:
                with st.spinner(f"Processing {f.name}..."):
                    result = process_file(f, excl_df_json)

                if result is None:
                    continue

                st.success(f"✓ {f.name}")
                st.dataframe(result['Summary'], use_container_width=True)

                try:
                    excel_bytes = write_excel(result)
                    out_name = f"CLEANED_{f.name}"
                    st.download_button(
                        label=f"⬇ Download {out_name} (Sheets 1–5 + Summary)",
                        data=excel_bytes,
                        file_name=out_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_excel_{f.name}"
                    )
                except Exception as e:
                    st.error(f"Excel generation failed: {e}")

                excl_sheet = result.get('6 Excluded Items Review')
                if excl_sheet is not None and len(excl_sheet):
                    csv_bytes = excl_sheet.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"⬇ Download Excluded Items ({len(excl_sheet):,} rows) — CSV",
                        data=csv_bytes,
                        file_name=f"EXCLUDED_{f.name.replace('.xlsx', '.csv')}",
                        mime="text/csv",
                        key=f"dl_csv_{f.name}"
                    )

st.markdown('</div>', unsafe_allow_html=True)
