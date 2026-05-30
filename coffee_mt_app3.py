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
    background: #ef44440d !important; border: 1px solid #ef444433 !important;
    border-radius: 2px !important;
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

SOLUBLE_KEYWORDS = [
    'INSTANT COFFEE', 'SOLUBLE COFFEE', 'SPRAY DRIED COFFEE',
    'FREEZE DRIED COFFEE', 'AGGLOMERATED COFFEE', 'AGGLOMERATED INSTANT',
    'FREEZE-DRIED COFFEE', 'SPRAY-DRIED COFFEE', 'COFFEE EXTRACT POWDER',
    'COFFEE PREMIX', 'NESCAFE', 'BRU INSTANT', 'SUNRISE EXTRA',
]
sol_pattern = '|'.join(re.escape(k) for k in SOLUBLE_KEYWORDS)

CHICORY_WRONG_HSN_KEYWORDS = ['CHICORY', 'CHICCORY']
chic_wrong_pat = '|'.join(re.escape(k) for k in CHICORY_WRONG_HSN_KEYWORDS)

# ── Admin / reference row patterns ──────────────────────────────
_ADMIN_PATTERNS = re.compile(
    r'\b(?:GSTIN(?=\W)|GSTN(?=\W)|GST\s+NO(?=\W)'
    r'|TAX\s+INV(?:OICE)?|INV\s*NO|INVOICE\s*NO'
    r'|ICO\s+SI\s+NUMBER|ICO\s+MARK\s+NO|PERMIT\s+NUMBER'
    r'|REF\s*NO\.?:'
    # Customs declaration boilerplate
    r'|REBATE\s+OBTAINED|SERVICE\s+TAX\s+PAID'
    r'|ON\s+THE\s+GROUND\s+THAT|SPECIFIED\s+SERVICES'
    r'|IN\s+ANY\s+OTHER\s+MANNER|THEGROUND\s+THAT'
    r'|LESSTHAN\s+THE|WE\s+DECLARE\s+THAT'
    r'|WE\s+HEREBY\s+DECLARE|ADMISSIBLE\s+UNDER'
    r'|CHAPTER\s*3\s+OF\s+FTP|BENEFITS\s+AS\s+ADMISSIBLE'
    r'|THESPECIFIED\s+SERVICES|OFRATE\s+SPECIFIED'
    r'|ON\s+THE\s+BASIS\s+OF\s*RATE|FREE\s+ON\s+BOARD\s*\(FOB\)'
    r'|NO\s+FURTHER\s+REBATE|IN\s+RESPECT\s+OF\s+THE\s+SPECIFIED'
    r'|UNDER\s+PROCEDURE\s+SPECIFIED|PARAGRAPH\s+3'
    r'|VALUE\s+OF\s+THE\s+SAID\s+GOODS|DECLARED\s+FREE\s+ON\s+BOARD'
    r'|HAVEBEEN\s+FULFILLED|CONDITIONS\s+OF\s+THE\s+NOTIFICATION'
    r'|ICO\s+REFERENCE|PERMIT\s*/\s*ICO\s+NO'
    r'|CHAPTER\s+3\s+BENEFITS|APPENDIX\s+37A'
    r'|VIDE\s*SL\s*\.?\s*NO|VIDESL\s*\.?\s*NO'
    r'|TABLE\s+2\s+OF\s+APPENDIX|I\s*/\s*WE\s+ARE\s+CLAIMING'
    r'|WE\s+ARE\s+CLAIMING\s+CHAPTER)',
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

# ── Structural legal boilerplate detector ────────────────────────
# Catches future variants of customs declaration text automatically
# using scoring across four independent signals. Product signal
# always overrides — a row with a brand name or weight is never flagged.
_LEGAL_VOCAB = {
    'NOTIFICATION', 'FULFILLED', 'CLAIMED', 'CLAIMING', 'ADMISSIBLE',
    'PARAGRAPH', 'APPENDIX', 'PROCEDURE', 'DECLARED', 'DECLARATION',
    'BENEFITS', 'REBATE', 'OBTAINED', 'PERCENTAGE', 'SCHEDULE',
    'THEREUNDER', 'AFORESAID', 'HEREIN', 'THEREOF', 'WHEREAS',
    'NOTWITHSTANDING', 'PURSUANT', 'UNDERTAKE', 'HEREBY',
    'CHAPTER', 'VIDE', 'VIDESL', 'HAVEBEEN', 'THESPECIFIED',
    'OFRATE', 'THEGROUND', 'LESSTHAN',
    'REFERENCE', 'SPECIFIED', 'SERVICES', 'PERMIT', 'DECLARE',
    'CLAIM', 'CONDITIONS', 'MANNER', 'GROUND', 'FURTHER', 'RESPECT',
}
_LEGAL_STARTERS = re.compile(
    r'^\s*(?:I{1,3}V?|VI{0,3}|I\s*/\s*WE\b'
    r'|WE\s+(?:ARE|HEREBY|SHALL|DECLARE)\b'
    r'|THE\s+\w+\s+OF\b'
    r'|ON\s+THE\s+(?:\w+\s+)?(?:OF|THAT|SERVICES)\b'
    r'|IN\s+(?:ANY|RESPECT|THE)\b'
    r'|ICO\s+REFERENCE|PERMIT\s*/\s*ICO'
    r')\s*[):]?,?\s*',
    re.IGNORECASE,
)
_ICO_PERMIT_PAT = re.compile(r'ICO\s+REFERENCE|PERMIT\s*/\s*ICO\s+NO', re.IGNORECASE)
_PRODUCT_SIGNAL_PAT = re.compile(
    r'\b(?:\d+\s*(?:GMS?|KGS?|GM|G\b|ML|LTR|NOS?|PCS?|CTN|BAGS?)'
    r'|(?:INSTANT|SOLUBLE|SPRAY\s+DRIED|FREEZE\s+DRIED|AGGLOMERATED)\s+COFFEE'
    r'|NESCAFE|NESTLE|BRU\b|SUNRISE|NARASUS|LEVISTA|COTHAS|CONTINENTAL'
    r'|TATA\s+COFFEE|DAVIDOFF|LAVAZZA|ILLY\b|KOPIKO|CHICORY|PREMIX|CAPPUCCINO)',
    re.IGNORECASE,
)

def _is_legal_boilerplate(desc):
    if not desc or len(str(desc).strip()) < 5:
        return False
    d = str(desc).upper().strip()
    if _PRODUCT_SIGNAL_PAT.search(d):
        return False
    if _ICO_PERMIT_PAT.search(d):
        return True
    tokens = d.split()
    n_tokens = len(tokens)
    clean_tokens = [re.sub(r'[^A-Z]', '', t) for t in tokens]
    legal_hits = sum(1 for t in clean_tokens if t in _LEGAL_VOCAB)
    score = 0
    if _LEGAL_STARTERS.search(d):
        score += 1
    if legal_hits >= 2:
        score += 1
    has_weight_number = bool(re.search(r'\d+\s*(?:GMS?|KGS?|GM|ML|NOS?|PCS?)', d))
    if n_tokens > 7 and not has_weight_number:
        score += 1
    if re.match(r'^\s*I{1,3}[)]\s', d) or re.match(r'^\s*II+[)]\s', d):
        score += 1
    if n_tokens <= 6 and d.rstrip().endswith(';') and legal_hits >= 1:
        score += 2
    return score >= 2

# ── Hardcoded non-soluble product type pattern ───────────────────
_HARDCODED_EXCL_PAT = re.compile(
    r'\b(?:'
    r'CHUKKU|CHUKKUKAPPI|SUKKU|KAPI(?!NO)|KAPPI|KAAPI'
    r'|GINGER\s+COFFEE|FILTER\s+COFFEE(?:\s+POWDER)?'
    r'|GROUND\s+COFFEE|ROASTED\s+COFFEE'
    r'|COLD\s+COFFEE|LIQUID\s+COFFEE|DECOCTION'
    r'|COLD\s+BREWED(?:\s+COFFEE(?:\s+CONCENTRATE)?)?'
    r'|FRAPPE'
    r'|INSTANT\s+TEA|MASALA\s+TEA|MASALA\s+CHAI'
    r'|SPRAY\s+DRIED\s+BLACK\s+TEA(?:\s+EXTRACT)?'
    r'|GREEN\s+COFFEE\s+BEAN(?:\s+EXTRACT)?'
    r'|GREEN\s+COFFEE\s+EXTRACT'
    r'|GREEN\s+COFFEE\s+ROBUSTA'
    r'|COFFEE\s+BEAN\s+EXTRACT'
    r'|COFFEE\s+BERRY\s+EXTRACT'
    r'|COFFEE\s+OIL'
    r'|CAFFEINE\s+ANHYDROUS|NATURAL\s+CAFFEINE'
    r'|CHLOROGENIC\s+ACID'
    r'|DOLCE\s+GUSTO|NESPRESSO\s+PODS'
    r')\b',
    re.IGNORECASE,
)

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
    kw_col  = excl_df['KEYWORD'].astype(str).str.upper().str.strip() if has_kw else pd.Series([''] * len(excl_df))
    hsn_col = (excl_df['HSN_FILTER'].astype(str).str.strip()
               .str.replace(r'\.0$', '', regex=True)
               if has_hsn else pd.Series([''] * len(excl_df)))
    rsn_col = excl_df['REASON'].astype(str) if has_rsn else pd.Series(['Exclusion list'] * len(excl_df))
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

    # Step 0 — admin / reference rows (regex patterns)
    _mark(desc.str.contains(_ADMIN_PATTERNS, na=False), 'Administrative/reference row')

    # Step 0a — structural legal boilerplate detector
    not_yet = ~pd.Series(excluded, index=df.index)
    legal_mask = not_yet & desc.apply(_is_legal_boilerplate)
    _mark(legal_mask, 'Legal/customs declaration boilerplate')

    # Step 0b — merchandise
    not_yet = ~pd.Series(excluded, index=df.index)
    _mark(not_yet & desc.str.contains(_MERCH_PATTERNS, na=False), 'Merchandise giveaway')

    # Step 0c — standalone mug with no coffee signal
    not_yet = ~pd.Series(excluded, index=df.index)
    mug_hit = not_yet & desc.str.contains(r'\bMUG\b', na=False)
    no_sig  = ~desc.str.contains(_STRICT_COFFEE_SIGNAL, na=False)
    _mark(mug_hit & no_sig, 'Merchandise giveaway — standalone mug')

    # Step 0d — hardcoded non-soluble product types
    not_yet = ~pd.Series(excluded, index=df.index)
    _mark(not_yet & desc.str.contains(_HARDCODED_EXCL_PAT, na=False),
          'Hardcoded structural exclusion — not soluble coffee')

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
                        reason[loc] = rsn
                        break
                excluded[loc] = True

    # Step 2 — user HSN-specific keywords
    for hsn_str, kw_dict in excl_hsn_kws.items():
        hsn_mask = (hsn_s == hsn_str) & (~pd.Series(excluded, index=df.index))
        if not hsn_mask.any():
            continue
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
        if not not_yet.any():
            break
        kw_hit   = not_yet & desc.str.contains(re.escape(kw), na=False)
        low_qty  = qty_mt < thr
        junk_hit = kw_hit & low_qty
        _mark(junk_hit, rsn)
        not_yet  = not_yet & ~junk_hit

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

def safe_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip().upper()

KNOWN_BRANDS = [
    (r'NESCAFE.*SUNRISE|SUNRISE.*NESCAFE|SUNRISE.*REGULAR|SUNRISE EXTRA|SUNRISE BLENDED|SUNRISE INSTA|SUNRISE COFFEE|SUNRISE.*PREMIUM|SUNRISE\s+BRAND', 70, 30, 'CONFIRMED', 'Nestle Professional listing'),
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
    # Only match when numbers sum to 100 — prevents permit numbers
    # like '67/28' (sum=95) being misread as blend ratios.
    desc_up = safe_str(desc_up)
    for m in re.finditer(r'\\b(\\d{2})\\s*([:/])\\s*(\\d{2})\\b', desc_up):
        a, b = int(m.group(1)), int(m.group(3))
        if a + b == 100:
            return a, b
    return None, None

def classify_chicory(desc_up):
    if pd.isna(desc_up):
        desc_up = ""
    else:
        desc_up = str(desc_up).upper()

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

CHICORY_SIGNAL_PAT = re.compile(
    r'CHICORY|CHICCORY|CICCORY|RICORY'
    # Explicit blend ratios that sum to 100 — avoids matching permit numbers like 67/28
    r'|\b(?:50[:/]50|60[:/]40|40[:/]60|70[:/]30|30[:/]70|80[:/]20|20[:/]80|75[:/]25|25[:/]75|65[:/]35|35[:/]65|55[:/]45|45[:/]55|53[:/]47|47[:/]53|85[:/]15|15[:/]85|90[:/]10|10[:/]90)\b'
    # Sunrise variants — all chicory blends (Nestle Professional)
    r'|NESCAFE.*SUNRISE|SUNRISE.*NESCAFE'
    r'|SUNRISE EXTRA|SUNRISE.*BLENDED|SUNRISE.*INSTA|SUNRISE.*PREMIUM'
    r'|SUNRISE COFFEE|SUNRISE.*REGULAR'
    # BRU chicory blends (HUL)
    r'|BRU INSTANT|BRU.*OPTIMA|BRU.*OPTM|BRU.*SUPER STRONG|BRU STRONG'
    r'|BRU.*PLATINA|BRU.*AROMA|BRU.*INST(?!.*GOLD)'
    r'|BRU.*GREEN LABEL|BRU.*SELECT'
    # Tata Coffee chicory blends
    r'|TATA.*GRAND'
    # Continental chicory blends
    r'|CONTINENTAL.*MALGUDI|CONTINENTAL.*XTRA|CONTINENTAL.*STRONG'
    # Narasus chicory blends
    r'|NARASUS.*UDHAYAM|NARASUS.*UDHAIYAM|NARASUS.*DELITE|NARASUS.*BESH SUKKU'
    # Levista chicory blends
    r'|LEVISTA.*CLASSIC|LEVISTA.*[678]0'
    # Cothas chicory blends
    r'|COTHAS.*SPECIAL|COTHAS.*PREMIUM|COTHAS.*80'
    # KDC ratio blends
    r'|KDC.*[678]0',
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
    qty  = row.get('STANDARD QUANTITY')
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()
    if pd.isna(qty):
        return np.nan, 'BLANK'
    try:
        qty = float(qty)
    except Exception:
        return np.nan, 'BLANK'

    clean = _STOP_PAT_MT.sub(' ', desc).strip()
    clean = re.sub(r'\s+', ' ', clean)
    clean = clean.replace(' X ', 'X').replace(' x ', 'X').replace('*', 'X')

    for pat, fn in [
        for pat, fn in [
    (r'(\d+(?:\.\d+)?)\s*KGS?\s*NET',      lambda m: float(m.group(1)) / 1000),
    (r'(\d+(?:\.\d+)?)KGSX(\d+)',           lambda m: float(m.group(1)) * float(m.group(2)) / 1000),
    (r'(\d+)X(\d+(?:\.\d+)?)KG\b',         lambda m: float(m.group(1)) * float(m.group(2)) / 1000),
    (r'(\d+(?:\.\d+)?)\s*KGS?\s*NET',      lambda m: float(m.group(1)) / 1000),
]:
    ]:
        m = re.search(pat, clean, re.IGNORECASE)
        if m:
            return qty * fn(m), 'PARSED'

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
        if m:
            return qty * fn(m), 'PARSED'

    for pat, div in [
        (r'(\d+(?:\.\d+)?)\s*GRAMS?\b', 1e6),
        (r'(\d+(?:\.\d+)?)\s*GRM\b',    1e6),
    ]:
        m = re.search(pat, clean, re.IGNORECASE)
        if m:
            return qty * float(m.group(1)) / div, 'PARSED'

    for suffix, div in [('GMS', 1e6), ('GM', 1e6), ('G', 1e6), ('KG', 1.0), ('ML', 1e6)]:
        vals = re.findall(r'(\d+(?:\.\d+)?)\s*' + suffix + r'\b', clean, re.IGNORECASE)
        if vals:
            val = float(vals[-1])
            if suffix == 'G' and val >= 5000:
                continue
            factor = val / div if suffix != 'KG' else val
            return qty * factor, 'PARSED'

    return np.nan, 'BLANK'

def convert_mt_vectorised(df):
    qty  = pd.to_numeric(df.get('STANDARD QUANTITY', pd.Series(dtype=float)), errors='coerce')
    unit = df.get('STANDARD QUANTITY UNIT', pd.Series(dtype=str)).astype(str).str.upper().str.strip()

    is_blank = qty.isna()
    is_kgs   = unit.isin(DIRECT_KG)   & ~is_blank
    is_mt    = unit.isin(DIRECT_MT_U) & ~is_blank
    is_ml    = unit.isin(DIRECT_ML)   & ~is_blank
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
        parsed = df[is_parse].apply(_convert_row_to_mt, axis=1)
        mt_vals[is_parse] = parsed.apply(lambda x: x[0]).astype(float).values
        status[is_parse]  = parsed.apply(lambda x: x[1]).values

    return mt_vals, status


# ================================================================
# SECTION F — WATERFALL MT IMPUTATION TIERS
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
                matched = actual[c.strip().lower()]
                break
        if not matched:
            for c in candidates:
                cl = c.strip().lower()
                for al, ao in actual.items():
                    if cl in al or al in cl:
                        matched = ao
                        break
                if matched:
                    break
        out[key] = matched
    return out

def _parse_unit_canonical(u):
    if pd.isna(u):
        return "UNKNOWN"
    u = str(u).strip().upper()
    if u in WEIGHT_UNIT_MAP:
        return u
    for key in PACKAGING_BENCHMARKS:
        if key in u:
            return key
    return u

def _bag_kg_from_price(up):
    if pd.isna(up) or up <= 0:
        return 60.0
    if 2.5 <= up / 60.0 <= 10.0:
        return 60.0
    for bkg in [50, 25, 10, 5, 1]:
        if 2.0 <= up / bkg <= 15.0:
            return float(bkg)
    return 60.0

def _tier1(row, cols, cfg):
    qc = cols.get("col_qty")
    uc = cols.get("col_unit")
    fc = cols.get("col_fob")
    pc = cols.get("col_unit_price")
    if not qc or not uc:
        return None
    qty      = row.get(qc)
    unit_raw = str(row.get(uc, "")).strip().upper()
    if pd.isna(qty) or float(qty) <= 0:
        return None
    qty       = float(qty)
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

def _to_g(val, unit_str):
    key = unit_str.upper().rstrip("S")
    return val * _UNIT_TO_G.get(key, _UNIT_TO_G.get(unit_str.upper(), 1.0))

def _extract_carton_kg(desc):
    if not desc or (isinstance(desc, float) and np.isnan(desc)):
        return None, None, None
    d = str(desc).upper().strip()
    if not d or any(p.search(d) for p in _BULK_PATS):
        return None, None, None
    _MIN, _MAX = 0.001, 50.0
    for regex, fn, label, conf in [
        (_P3,       lambda m: _to_g(float(m[-1][0]), m[-1][1]) / 1000.0,                          "P3_NET_WT", "HIGH"),
        (_P1_MULTI, lambda m: float(m[-1][0]) * _to_g(float(m[-1][1]), m[-1][2]) * float(m[-1][3]) / 1000.0, "P1_MULTI", "HIGH"),
        (_P1,       lambda m: float(m[-1][0]) * _to_g(float(m[-1][1]), m[-1][2]) / 1000.0,        "P1_NxW",   "HIGH"),
        (_P2,       lambda m: _to_g(float(m[-1][0]), m[-1][1]) * float(m[-1][2]) / 1000.0,        "P2_WxN",   "HIGH"),
        (_P4,       lambda m: _to_g(float(m[-1][0]), m[-1][1]) * float(m[-1][2]) / 1000.0,        "P4_PAREN", "MEDIUM"),
    ]:
        hits = regex.findall(d)
        if hits:
            try:
                kg = fn(hits)
                if _MIN <= kg <= _MAX:
                    return kg, label, conf
            except Exception:
                pass
    return None, None, None

def _tier1b(row, cols, cfg):
    qc = cols.get("col_qty")
    dc = cols.get("col_desc")
    if not qc or not dc:
        return None
    qty  = row.get(qc)
    desc = row.get(dc, "")
    if pd.isna(qty):
        return None
    qty = float(qty)
    kg, pattern, conf = _extract_carton_kg(desc)
    if kg is None:
        return None
    if qty == 0:
        mt = kg / 1000.0
        return (mt, f"T1B_DESC_{pattern}_ZERO_QTY", mt * 0.80, mt * 1.20)
    if qty <= 0:
        return None
    mt = qty * kg / 1000.0
    if mt < cfg["min_plausible_mt"] or mt > cfg["max_plausible_mt"]:
        return None
    lo, hi = (mt * 0.95, mt * 1.05) if conf == "HIGH" else (mt * 0.85, mt * 1.15)
    return (mt, f"T1B_DESC_{pattern}", lo, hi)

def _desc_tokens(desc):
    if not desc or (isinstance(desc, float) and np.isnan(desc)):
        return set()
    return {t for t in re.sub(r'[^A-Z0-9\s]', ' ', str(desc).upper()).split()
            if len(t) >= 3 and t not in _STOP_PEER}

def _jaccard(a, b):
    ta, tb = _desc_tokens(a), _desc_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def _build_peer_index(df, cols):
    cm    = cols.get("col_mt")
    cq    = cols.get("col_qty")
    ce    = cols.get("col_exporter")
    cp    = cols.get("col_port")
    ch    = cols.get("col_hs")
    cd    = cols.get("col_desc")
    cdate = cols.get("col_date")
    cu    = cols.get("col_unit")
    if not all([cm, cq, ce, ch, cd]):
        return {}, {}
    base = df[df[cm].notna() & (df[cm] > 0) & df[cq].notna() & (df[cq] > 0)].copy()
    if base.empty or not cdate or cdate not in base.columns:
        return {}, {}
    base["_period"] = pd.to_datetime(base[cdate], errors="coerce").dt.to_period("M")
    base["_hs6"]    = base[ch].astype(str).str.replace(r'\D', '', regex=True).str[:6]
    base["_mpu"]    = base[cm] / base[cq]
    exp_idx  = {}
    port_idx = {}
    for _, r in base.iterrows():
        entry = (r["_period"], r[cd], r["_mpu"], r.get(cu, ""))
        exp_idx.setdefault((str(r[ce]).strip(), r["_hs6"]), []).append(entry)
        if cp:
            port_idx.setdefault((str(r.get(cp, "")).strip(), r["_hs6"]), []).append(entry)
    return exp_idx, port_idx

def _tier1c(row, exp_idx, port_idx, cols, cfg):
    dc    = cols.get("col_desc")
    qc    = cols.get("col_qty")
    ec    = cols.get("col_exporter")
    pc    = cols.get("col_port")
    hc    = cols.get("col_hs")
    datec = cols.get("col_date")
    desc  = row.get(dc, "") if dc else ""
    if not any(b in str(desc).upper() for b in _BRAND_KWS_IMP):
        return None
    if not qc:
        return None
    qty = row.get(qc)
    if pd.isna(qty) or float(qty) <= 0:
        return None
    qty  = float(qty)
    hs6  = str(row.get(hc, "")).replace('.', '')[:6] if hc else ""
    exp  = str(row.get(ec, "")).strip() if ec else ""
    port = str(row.get(pc, "")).strip() if pc else ""
    try:
        tp = pd.Period(row[datec], "M") if (datec and datec in row and pd.notna(row.get(datec))) else None
    except Exception:
        tp = None

    def _gap(p):
        try:
            return abs((p - tp).n) if tp and p else 999
        except Exception:
            return 999

    is_bare = len(_desc_tokens(desc)) <= 2
    matched = [b for b in _BRAND_KWS_IMP if b in str(desc).upper()]
    best_score, best_mpu, best_src = -1, None, None

    for key, src in [((exp, hs6), "exporter"), ((port, hs6), "port")]:
        idx        = exp_idx if src == "exporter" else port_idx
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
                if _gap(per) > 3:
                    continue
                sim = _jaccard(desc, pd_)
                if sim < 0.35:
                    continue
                score = sim * max(0.4, 1.0 - _gap(per) * 0.15)
                if score > best_score:
                    best_score, best_mpu, best_src = score, mpu, src

    if not best_mpu or best_mpu <= 0:
        return None
    mt = qty * best_mpu
    if mt < cfg["min_plausible_mt"] or mt > cfg["max_plausible_mt"]:
        return None
    if "BARE" in str(best_src):
        lo   = mt * 0.60
        hi   = mt * 1.40
        flag = f"T1C_PEER_{best_src.replace('_BARE','').upper()}_BARE_BRAND"
    else:
        margin = 0.15 if "exporter" in best_src else 0.25
        lo     = mt * (1 - margin)
        hi     = mt * (1 + margin)
        flag   = f"T1C_PEER_{best_src.upper()}"
    return mt, flag, lo, hi

def _build_suv_table(df, cols, cfg):
    cm = cols.get("col_mt")
    cf = cols.get("col_fob")
    ch = cols.get("col_hs")
    cp = cols.get("col_port")
    cd = cols.get("col_date")
    if not all([cm, cf, ch, cp]):
        return {}
    base = df[df[cm].notna() & (df[cm] > 0) & df[cf].notna() & (df[cf] > 0)].copy()
    if base.empty:
        return {}
    base["_uv"]  = base[cf] / base[cm]
    base["_hs6"] = base[ch].astype(str).str.replace(r'\D', '', regex=True).str[:6]
    base["_per"] = (pd.to_datetime(base[cd], errors="coerce").dt.to_period("M").astype(str)
                    if cd and cd in base.columns else "ALL")
    suv = {}
    for (hs6, port, per), grp in base.groupby(["_hs6", cp, "_per"]):
        uv = grp["_uv"].dropna()
        uv = uv[(uv > 0) & np.isfinite(uv)]
        n  = len(uv)
        if n < cfg["suv_min_obs_low"]:
            continue
        med = float(np.median(uv))
        suv[(hs6, port, per)] = {"suv": med, "n": n}
    return suv

def _tier2(row, suv_table, cols, cfg):
    fc = cols.get("col_fob")
    hc = cols.get("col_hs")
    pc = cols.get("col_port")
    dc = cols.get("col_date")
    if not fc:
        return None
    fob = row.get(fc)
    if pd.isna(fob) or fob <= 0:
        return None
    hs6  = str(row.get(hc, "")).replace('.', '')[:6] if hc else ""
    port = str(row.get(pc, "")).strip() if pc else ""
    try:
        per = pd.Period(row[dc], "M").strftime("%Y-%m") if (dc and pd.notna(row.get(dc))) else "ALL"
    except Exception:
        per = "ALL"
    entry = suv_table.get((hs6, port, per))
    if entry is None:
        for (h, p, pp), e in suv_table.items():
            if h == hs6 and pp == per and e["n"] >= cfg["suv_min_obs_low"]:
                entry = e
                break
    if entry is None:
        return None
    suv = entry["suv"]
    if suv <= 0:
        return None
    mt = fob / suv
    if mt < cfg["min_plausible_mt"] or mt > cfg["max_plausible_mt"]:
        return None
    sg = suv * 0.3
    return (mt, "T2_SUV_HS6", suv, entry["n"], fob / (suv + sg), fob / max(suv - sg, suv * 0.1))

def _detect_ico_group(hs_val):
    s = str(hs_val).replace('.', '').strip()
    if s[:4] == "2101":  return "SOLUBLE"
    if s[:5] == "09012": return "ROASTED"
    if s[:4] == "0901":  return "GREEN"
    return "DEFAULT"

def _build_temporal_index(df, cols):
    cm = cols.get("col_mt")
    ce = cols.get("col_exporter")
    ch = cols.get("col_hs")
    cd = cols.get("col_date")
    if not all([cm, ce, ch, cd]) or cd not in df.columns:
        return {}
    base = df[df[cm].notna() & (df[cm] > 0)].copy()
    base["_per"] = pd.to_datetime(base[cd], errors="coerce").dt.to_period("M")
    base["_hs4"] = base[ch].astype(str).str.replace(r'\D', '', regex=True).str[:4]
    t = {}
    for (exp, hs4), grp in base.groupby([ce, "_hs4"]):
        t[(str(exp).strip(), hs4)] = grp.groupby("_per")[cm].median().sort_index()
    return t

def _tier3(row, temporal_idx, cols, cfg):
    ce  = cols.get("col_exporter")
    ch  = cols.get("col_hs")
    cf  = cols.get("col_fob")
    cd  = cols.get("col_date")
    exp = str(row.get(ce, "")).strip() if ce else ""
    hs4 = str(row.get(ch, "")).replace('.', '')[:4] if ch else ""
    fob = row.get(cf) if cf else None

    if cd and cd in row and pd.notna(row.get(cd)):
        key = (exp, hs4)
        if key in temporal_idx:
            try:
                target = pd.Period(row[cd], "M")
                diffs  = [(abs((p - target).n), v) for p, v in temporal_idx[key].items()
                          if abs((p - target).n) <= 3]
                if diffs:
                    diffs.sort()
                    nd, nmt = diffs[0]
                    mt = nmt * max(0.5, 1.0 - nd * 0.1)
                    return (mt, "T3_INTERPOLATED", None, 0, mt * 0.7, mt * 1.3)
            except Exception:
                pass

    if fob is not None and pd.notna(fob) and fob > 0:
        group   = _detect_ico_group(row.get(ch, ""))
        ico_suv = ICO_PRICES.get(group, ICO_PRICES["DEFAULT"])
        mt      = fob / ico_suv
        if cfg["min_plausible_mt"] <= mt <= cfg["max_plausible_mt"]:
            return (mt, "T3_ICO_ANCHOR", ico_suv, 0, mt * 0.6, mt * 1.4)

    return (None, "IRRECOVERABLE", None, 0, None, None)

def run_imputation(df_in):
    df   = df_in.copy()
    cols = _resolve_imp_cols(df)
    cfg  = IMP_CFG.copy()
    cm   = cols.get("col_mt")

    if not cm or cm not in df.columns:
        for c in ["MT", "MT_WEIGHT", "TOTAL_MT"]:
            if c in df.columns:
                cm = c
                cols["col_mt"] = c
                break
    if not cm or cm not in df.columns:
        return df, {"error": "MT column not found"}

    cd = cols.get("col_date")
    if cd and cd in df.columns:
        df[cd] = pd.to_datetime(df[cd], errors="coerce")

    df["MT_FINAL"]       = np.nan
    df["MT_FLAG"]        = ""
    df["MT_SOURCE_TIER"] = -1
    df["MT_LOWER"]       = np.nan
    df["MT_UPPER"]       = np.nan

    has_mt = df[cm].notna() & (df[cm] > 0)
    df.loc[has_mt, "MT_FINAL"]       = df.loc[has_mt, cm]
    df.loc[has_mt, "MT_FLAG"]        = "OBSERVED"
    df.loc[has_mt, "MT_SOURCE_TIER"] = 0

    suv_table             = _build_suv_table(df, cols, cfg)
    exp_idx, port_idx     = _build_peer_index(df, cols)
    temporal_idx          = _build_temporal_index(df, cols)

    cs         = cols.get("col_mt_status")
    blank_mask = df[cm].isna() | (df[cm] == 0)
    if cs and cs in df.columns:
        blank_mask = blank_mask | (df[cs].astype(str).str.strip().str.upper() == "BLANK")

    counts = {"OBSERVED": int(has_mt.sum()), "T1": 0, "T1B": 0, "T1C": 0, "T2": 0, "T3": 0, "IRRECOVERABLE": 0}

    for idx, row in df[blank_mask].iterrows():
        result = _tier1(row, cols, cfg)
        if result:
            mt, flag, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 1
            df.at[idx, "MT_LOWER"] = lo; df.at[idx, "MT_UPPER"] = hi
            counts["T1"] += 1; continue

        result = _tier1b(row, cols, cfg)
        if result:
            mt, flag, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 1
            df.at[idx, "MT_LOWER"] = lo; df.at[idx, "MT_UPPER"] = hi
            counts["T1B"] += 1; continue

        result = _tier1c(row, exp_idx, port_idx, cols, cfg)
        if result:
            mt, flag, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 1
            df.at[idx, "MT_LOWER"] = lo; df.at[idx, "MT_UPPER"] = hi
            counts["T1C"] += 1; continue

        result = _tier2(row, suv_table, cols, cfg)
        if result:
            mt, flag, suv, n, lo, hi = result
            df.at[idx, "MT_FINAL"] = mt; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 2
            df.at[idx, "MT_LOWER"] = lo; df.at[idx, "MT_UPPER"] = hi
            counts["T2"] += 1; continue

        result = _tier3(row, temporal_idx, cols, cfg)
        mt, flag, suv, n, lo, hi = result
        if flag == "IRRECOVERABLE":
            df.at[idx, "MT_FLAG"] = "IRRECOVERABLE"
            df.at[idx, "MT_SOURCE_TIER"] = 3
            counts["IRRECOVERABLE"] += 1
        else:
            df.at[idx, "MT_FINAL"] = mt; df.at[idx, "MT_FLAG"] = flag
            df.at[idx, "MT_SOURCE_TIER"] = 3
            df.at[idx, "MT_LOWER"] = lo; df.at[idx, "MT_UPPER"] = hi
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

def _find_header_row(file_obj, engine):
    """
    Scan first 15 rows to find the real header row.
    CYBEX files sometimes have 5-6 rows of company branding above the
    actual column headers.
    """
    raw = pd.read_excel(file_obj, header=None, nrows=15, engine=engine)
    for i, row in raw.iterrows():
        vals   = [str(v).upper().strip() for v in row if pd.notna(v)]
        has_hs = any(('HS' in v and 'CODE' in v) or v in ('HS CODE', 'HSCODE', 'HSN CODE', 'HS') for v in vals)
        has_desc = any('DESC' in v or 'PRODUCT' in v for v in vals)
        if has_hs and has_desc:
            return i
    return 0


def process_file(file, excl_df_json):
    # ── Load ──────────────────────────────────────────────────────
    try:
        file.seek(0)
        hdr_row = _find_header_row(file, 'calamine')
        file.seek(0)
        df = pd.read_excel(file, header=hdr_row, engine='calamine')
    except Exception:
        try:
            file.seek(0)
            hdr_row = _find_header_row(file, 'openpyxl')
            file.seek(0)
            df = pd.read_excel(file, header=hdr_row, engine='openpyxl')
        except Exception:
            file.seek(0)
            df = pd.read_excel(file, engine='openpyxl')

    df.columns = df.columns.astype(str).str.strip()

    # ── Detect columns ────────────────────────────────────────────
    hs_col = (next((c for c in df.columns if 'HS' in c.upper() and 'CODE' in c.upper()), None)
              or next((c for c in df.columns if c.upper() in ('HS CODE', 'HSCODE', 'HSN CODE', 'HS')), None))
    desc_col = (next((c for c in df.columns if 'PRODUCT' in c.upper() and 'DESC' in c.upper()), None)
                or next((c for c in df.columns if 'DESC' in c.upper()), None))
    if not hs_col or not desc_col:
        st.error(f"Cannot find HS CODE or PRODUCT DESCRIPTION columns in **{file.name}**")
        return None

    # ── Helper columns ────────────────────────────────────────────
    df['_HSN_INT'] = norm_hsn_series(df[hs_col])
    df['_HSN_STR'] = df['_HSN_INT'].astype(str)

    # Build _DESC_UP: use desc_col, then fall back to any other PRODUCT DESC
    # column that has content when the primary is blank/NaN. Handles files
    # where 'PRODUCT DESCRIPTION' column is NaN but 'PRODUCT DESCRIPTION2'
    # carries the actual description (common in some CYBEX exports).
    # We check pd.isna() on the ORIGINAL column (before astype(str)) so that
    # np.float64(nan) values are correctly detected as blank.
    desc_raw = df[desc_col]
    is_blank  = desc_raw.isna() | (desc_raw.astype(str).str.strip() == '')
    desc_series = desc_raw.astype(str).str.strip()

    fallback_desc_cols = [
        c for c in df.columns
        if c != desc_col
        and 'DESC' in c.upper()
        and 'PRODUCT' in c.upper()
    ]
    for fb_col in fallback_desc_cols:
        fb_raw    = df[fb_col]
        fb_blank  = fb_raw.isna() | (fb_raw.astype(str).str.strip() == '')
        fb_series = fb_raw.astype(str).str.strip()
        # Only fill from fallback where primary is blank AND fallback has content
        desc_series = desc_series.where(~is_blank | fb_blank, fb_series)
        # Update blank mask for next fallback column
        is_blank = is_blank & fb_blank

    df['_DESC_UP'] = desc_series.str.upper().str.strip()
    df['_BUCKET']  = bucket_hsn_series(df['_HSN_INT'])

    # ── Exclusions ────────────────────────────────────────────────
    excl_global, excl_hsn = build_excl_list_lookup(excl_df_json)
    df['_EXCLUDED'], df['_EXCL_REASON'] = apply_exclusions(df, excl_global, excl_hsn)

    # ── Sheet 1: all valid soluble coffee rows ────────────────────
    correct_hsn      = df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX'])
    wrong_hsn_rescue = (
        ~df['_BUCKET'].isin(['SOLUBLE_COFFEE', 'CHICORY_PREMIX', 'CHICORY_ONLY'])
        & df['_DESC_UP'].str.contains(sol_pattern, na=False, regex=True)
    )
    in_sheet1 = (correct_hsn | wrong_hsn_rescue) & ~df['_EXCLUDED']
    df_s1     = df[in_sheet1].copy()

    if df_s1.empty:
        st.warning(f"No soluble coffee rows found in **{file.name}** after filtering.")
        return None

    # ── MT conversion: direct / parsed ───────────────────────────
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

    if rename_map:
        df_s1 = df_s1.rename(columns=rename_map)
    df_s1['MT'], df_s1['MT_STATUS'] = convert_mt_vectorised(df_s1)
    if rename_map:
        df_s1 = df_s1.rename(columns={v: k for k, v in rename_map.items()})

    # ── Waterfall imputation on still-blank MT rows ───────────────
    df_s1, counts = run_imputation(df_s1)

    # ── Chicory sub-classification (Sheets 2, 3, 4) ──────────────
    clf_results      = df_s1['_DESC_UP'].apply(classify_chicory)
    df_s1['_CHICORY_CAT'] = clf_results.apply(lambda x: x[0] if x else None)

    def _add_blend_cols(df_sub):
        df_sub    = df_sub.copy()
        local_clf = df_sub['_DESC_UP'].apply(classify_chicory)
        df_sub['COFFEE_PCT']  = local_clf.apply(lambda x: x[1] if x else None)
        df_sub['CHICORY_PCT'] = local_clf.apply(lambda x: x[2] if x else None)
        df_sub['CONFIDENCE']  = local_clf.apply(lambda x: x[3] if x else None)
        df_sub['BLEND_NOTES'] = local_clf.apply(lambda x: x[4] if x else None)
        return df_sub

    df_s2 = _add_blend_cols(df_s1[df_s1['_CHICORY_CAT'] == 'EXPLICIT'].copy())
    df_s3 = _add_blend_cols(df_s1[df_s1['_CHICORY_CAT'] == 'KNOWN_BRAND'].copy())

    s4_brand  = df_s1[df_s1['_CHICORY_CAT'] == 'ASSUMED'].copy()
    s4_signal = df_s1[
        df_s1['_CHICORY_CAT'].isna() &
        df_s1['_DESC_UP'].str.contains(CHICORY_SIGNAL_PAT, na=False)
    ].copy()
    df_s4 = _add_blend_cols(pd.concat([s4_brand, s4_signal], ignore_index=True))
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
            sheet1_pool = []   # accumulates Sheet 1 from each file for cross-year analysis

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

                # Tag this Sheet 1 with source filename and add to multi-file pool
                s1_tagged = s1.copy()
                s1_tagged['_SOURCE_FILE'] = f.name
                sheet1_pool.append(s1_tagged)

                total_rows = sum(v for k, v in counts.items() if k != "error")
                st.success(f"✓ Pipeline complete — {f.name}")

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

                mc1, mc2, mc3 = st.columns(3)
                mt_flag_col = "MT_FLAG" if "MT_FLAG" in s1.columns else None
                mt_obs = s1.loc[s1["MT_FLAG"] == "OBSERVED", "MT_FINAL"].sum() if mt_flag_col and "MT_FINAL" in s1 else 0
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

            # ================================================================
            # CROSS-FILE ANALYSIS MODULE
            # Pools Sheet 1 from every processed file and computes trend views.
            # Three views: chicory share, destination region, pure vs blend.
            # ================================================================
            if len(sheet1_pool) >= 1:
                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                st.markdown("""
                <div class="stage-header" style="margin-top: 28px">
                    <span class="stage-num">ANALYSIS</span>
                    <span class="stage-title">Multi-File Trend Analysis — Chicory Blending in Indian Soluble Coffee Exports</span>
                </div>
                """, unsafe_allow_html=True)

                # ── Pool all Sheet 1 dataframes ─────────────────────────────
                pooled = pd.concat(sheet1_pool, ignore_index=True)

                # Detect date column (CYBEX uses SBDATE, processed files use 'date')
                date_col = next((c for c in pooled.columns
                                 if c.upper() in ('SBDATE', 'DATE', 'SHIPMENT DATE', 'SB DATE')), None)
                if date_col is None:
                    date_col = next((c for c in pooled.columns if 'DATE' in c.upper()), None)

                # Detect destination region column
                region_col = next((c for c in pooled.columns
                                   if 'FOREIGN' in c.upper() and 'REGION' in c.upper()), None)
                country_col = next((c for c in pooled.columns
                                    if ('FOREIGN' in c.upper() and 'COUNTRY' in c.upper())
                                    and 'FINAL' in c.upper()), None)
                if not country_col:
                    country_col = next((c for c in pooled.columns
                                        if 'FOREIGN' in c.upper() and 'COUNTRY' in c.upper()), None)

                if not date_col or 'MT_FINAL' not in pooled.columns:
                    st.error("Analysis requires date and MT_FINAL columns — not all detected.")
                else:
                    # Parse date and build YYYY-MM bucket
                    pooled['_DATE'] = pd.to_datetime(pooled[date_col], errors='coerce')
                    pooled = pooled[pooled['_DATE'].notna()].copy()
                    pooled['_MONTH'] = pooled['_DATE'].dt.to_period('M').astype(str)
                    pooled['_MT'] = pd.to_numeric(pooled['MT_FINAL'], errors='coerce').fillna(0)

                    # Classify each row into 4 buckets based on _CHICORY_CAT
                    def _bucket(cat):
                        if cat == 'EXPLICIT':    return 'Chicory Explicit'
                        if cat == 'KNOWN_BRAND': return 'Chicory Known Brand'
                        if cat == 'ASSUMED':     return 'Chicory Assumed'
                        return 'Pure Coffee'
                    pooled['_BUCKET_CHIC'] = pooled.get('_CHICORY_CAT', pd.Series([None]*len(pooled))).apply(_bucket)

                    n_months  = pooled['_MONTH'].nunique()
                    n_files   = pooled['_SOURCE_FILE'].nunique()
                    total_mt  = pooled['_MT'].sum()
                    chic_mt   = pooled[pooled['_BUCKET_CHIC'] != 'Pure Coffee']['_MT'].sum()
                    chic_pct  = chic_mt / total_mt * 100 if total_mt > 0 else 0

                    # ── Top-level KPI cards ───────────────────────────────
                    k1, k2, k3, k4 = st.columns(4)
                    with k1:
                        st.markdown(f"""<div class="result-box">
                            <div class="result-box-label">Files Pooled</div>
                            <div class="result-mt">{n_files}</div>
                            <div class="result-mt-sub">{len(pooled):,} rows</div>
                        </div>""", unsafe_allow_html=True)
                    with k2:
                        st.markdown(f"""<div class="result-box">
                            <div class="result-box-label">Months Covered</div>
                            <div class="result-mt">{n_months}</div>
                            <div class="result-mt-sub">monthly bucket</div>
                        </div>""", unsafe_allow_html=True)
                    with k3:
                        st.markdown(f"""<div class="result-box">
                            <div class="result-box-label">Total Soluble MT</div>
                            <div class="result-mt">{total_mt:,.0f}</div>
                            <div class="result-mt-sub">across all files</div>
                        </div>""", unsafe_allow_html=True)
                    with k4:
                        st.markdown(f"""<div class="result-box">
                            <div class="result-box-label">Chicory Share</div>
                            <div class="result-mt">{chic_pct:.1f}%</div>
                            <div class="result-mt-sub">of total volume</div>
                        </div>""", unsafe_allow_html=True)

                    # ── View toggle ───────────────────────────────────────
                    st.markdown("<br>", unsafe_allow_html=True)
                    view = st.radio(
                        "Select trend view:",
                        ["Chicory Share Over Time", "Destination Region Mix", "Pure vs Blend Split by Month"],
                        horizontal=True,
                        key="analysis_view",
                    )

                    # ── View 1: Chicory Share Over Time ───────────────────
                    if view == "Chicory Share Over Time":
                        monthly = (pooled.groupby(['_MONTH', '_BUCKET_CHIC'])['_MT']
                                   .sum().unstack(fill_value=0).sort_index())

                        # Reorder columns: Pure first, then chicory tiers
                        col_order = ['Pure Coffee', 'Chicory Explicit', 'Chicory Known Brand', 'Chicory Assumed']
                        monthly = monthly.reindex(columns=[c for c in col_order if c in monthly.columns], fill_value=0)
                        monthly_total = monthly.sum(axis=1)
                        share = monthly.div(monthly_total, axis=0).fillna(0) * 100

                        # Two-panel chart: absolute MT (stacked bar) + % share (line)
                        import altair as alt
                        # Long-form for Altair
                        long_abs = monthly.reset_index().melt(id_vars='_MONTH', var_name='Category', value_name='MT')
                        chart_abs = (
                            alt.Chart(long_abs)
                            .mark_bar()
                            .encode(
                                x=alt.X('_MONTH:N', title='Month', sort=monthly.index.tolist()),
                                y=alt.Y('MT:Q', title='MT'),
                                color=alt.Color('Category:N',
                                                scale=alt.Scale(
                                                    domain=col_order,
                                                    range=['#00d4aa', '#3b82f6', '#f59e0b', '#a78bfa']),
                                                legend=alt.Legend(orient='bottom')),
                                tooltip=['_MONTH', 'Category', alt.Tooltip('MT:Q', format=',.1f')],
                            )
                            .properties(height=320, title='Volume by chicory category (MT, stacked)')
                        )
                        st.altair_chart(chart_abs, use_container_width=True)

                        # Chicory share % line
                        share['_TOTAL_CHIC'] = share.drop(columns=['Pure Coffee'], errors='ignore').sum(axis=1)
                        share_df = share[['_TOTAL_CHIC']].reset_index().rename(columns={'_TOTAL_CHIC': 'Chicory %'})
                        chart_share = (
                            alt.Chart(share_df)
                            .mark_line(point=True, color='#00d4aa', strokeWidth=2.5)
                            .encode(
                                x=alt.X('_MONTH:N', title='Month', sort=monthly.index.tolist()),
                                y=alt.Y('Chicory %:Q', title='Chicory share (%)', scale=alt.Scale(domain=[0, max(share_df['Chicory %'].max() * 1.15, 10)])),
                                tooltip=['_MONTH', alt.Tooltip('Chicory %:Q', format='.1f')],
                            )
                            .properties(height=260, title='Chicory share of total soluble exports (%)')
                        )
                        st.altair_chart(chart_share, use_container_width=True)

                        # Underlying data
                        with st.expander("View underlying data"):
                            display = monthly.copy()
                            display['Total MT'] = monthly_total
                            display['Chicory %'] = share['_TOTAL_CHIC'].round(2)
                            st.dataframe(display.style.format("{:,.1f}"), use_container_width=True)

                    # ── View 2: Destination Region Mix ────────────────────
                    elif view == "Destination Region Mix":
                        if not region_col and not country_col:
                            st.warning("No destination region/country column found in the data.")
                        else:
                            dest_col = region_col if region_col else country_col
                            dest_label = "Region" if region_col else "Country"
                            pooled['_DEST']    = pooled[dest_col].astype(str).str.strip().str.upper().replace('NAN', 'UNKNOWN')
                            pooled['_IS_CHIC'] = pooled['_BUCKET_CHIC'] != 'Pure Coffee'

                            # By destination — total MT, chicory MT, chicory share
                            grp = pooled.groupby('_DEST').agg(
                                total_mt=('_MT', 'sum'),
                                chic_mt =('_MT', lambda s: s[pooled.loc[s.index, '_IS_CHIC']].sum()),
                            )
                            grp['chic_pct'] = (grp['chic_mt'] / grp['total_mt'] * 100).fillna(0)
                            grp = grp.sort_values('total_mt', ascending=False).head(15)

                            import altair as alt
                            grp_reset = grp.reset_index()
                            chart_dest = (
                                alt.Chart(grp_reset)
                                .mark_bar()
                                .encode(
                                    y=alt.Y('_DEST:N', title=dest_label, sort='-x'),
                                    x=alt.X('total_mt:Q', title='Total MT'),
                                    color=alt.Color('chic_pct:Q',
                                                    title='Chicory %',
                                                    scale=alt.Scale(scheme='viridis')),
                                    tooltip=[alt.Tooltip('_DEST:N', title=dest_label),
                                             alt.Tooltip('total_mt:Q', format=',.1f', title='Total MT'),
                                             alt.Tooltip('chic_mt:Q',  format=',.1f', title='Chicory MT'),
                                             alt.Tooltip('chic_pct:Q', format='.1f',  title='Chicory %')],
                                )
                                .properties(height=420, title=f'Top 15 {dest_label.lower()}s by volume — coloured by chicory share')
                            )
                            st.altair_chart(chart_dest, use_container_width=True)

                            # Monthly trend per top-5 destinations
                            top5 = grp.head(5).index.tolist()
                            sub  = pooled[pooled['_DEST'].isin(top5)].copy()
                            sub_monthly = sub.groupby(['_MONTH', '_DEST'])['_MT'].sum().reset_index()
                            chart_trend = (
                                alt.Chart(sub_monthly)
                                .mark_line(point=True)
                                .encode(
                                    x=alt.X('_MONTH:N', title='Month'),
                                    y=alt.Y('_MT:Q', title='MT'),
                                    color=alt.Color('_DEST:N', title=dest_label),
                                    tooltip=['_MONTH', '_DEST', alt.Tooltip('_MT:Q', format=',.1f')],
                                )
                                .properties(height=320, title=f'Top 5 {dest_label.lower()}s — monthly volume trend')
                            )
                            st.altair_chart(chart_trend, use_container_width=True)

                            with st.expander("View underlying data"):
                                st.dataframe(grp.style.format({"total_mt": "{:,.1f}", "chic_mt": "{:,.1f}", "chic_pct": "{:.1f}"}),
                                             use_container_width=True)

                    # ── View 3: Pure vs Blend Split by Month ──────────────
                    else:
                        pooled['_SIMPLE_CAT'] = pooled['_BUCKET_CHIC'].apply(
                            lambda x: 'Pure Coffee' if x == 'Pure Coffee' else 'Chicory Blend'
                        )
                        monthly_split = (pooled.groupby(['_MONTH', '_SIMPLE_CAT'])['_MT']
                                         .sum().unstack(fill_value=0).sort_index())
                        for col in ['Pure Coffee', 'Chicory Blend']:
                            if col not in monthly_split.columns:
                                monthly_split[col] = 0
                        monthly_split = monthly_split[['Pure Coffee', 'Chicory Blend']]

                        import altair as alt
                        long_split = monthly_split.reset_index().melt(id_vars='_MONTH', var_name='Type', value_name='MT')
                        chart_split = (
                            alt.Chart(long_split)
                            .mark_bar()
                            .encode(
                                x=alt.X('_MONTH:N', title='Month', sort=monthly_split.index.tolist()),
                                y=alt.Y('MT:Q', title='MT'),
                                color=alt.Color('Type:N',
                                                scale=alt.Scale(domain=['Pure Coffee', 'Chicory Blend'],
                                                                range=['#00d4aa', '#a78bfa']),
                                                legend=alt.Legend(orient='bottom')),
                                tooltip=['_MONTH', 'Type', alt.Tooltip('MT:Q', format=',.1f')],
                            )
                            .properties(height=340, title='Pure coffee vs chicory blend — monthly volume (MT)')
                        )
                        st.altair_chart(chart_split, use_container_width=True)

                        # Stacked 100% normalised view
                        total_per_month = monthly_split.sum(axis=1)
                        norm = monthly_split.div(total_per_month, axis=0).fillna(0) * 100
                        long_norm = norm.reset_index().melt(id_vars='_MONTH', var_name='Type', value_name='Share')
                        chart_norm = (
                            alt.Chart(long_norm)
                            .mark_bar()
                            .encode(
                                x=alt.X('_MONTH:N', title='Month', sort=monthly_split.index.tolist()),
                                y=alt.Y('Share:Q', title='Share (%)', stack='normalize', scale=alt.Scale(domain=[0, 100])),
                                color=alt.Color('Type:N',
                                                scale=alt.Scale(domain=['Pure Coffee', 'Chicory Blend'],
                                                                range=['#00d4aa', '#a78bfa']),
                                                legend=alt.Legend(orient='bottom')),
                                tooltip=['_MONTH', 'Type', alt.Tooltip('Share:Q', format='.1f')],
                            )
                            .properties(height=260, title='Pure vs chicory blend — monthly share (%)')
                        )
                        st.altair_chart(chart_norm, use_container_width=True)

                        with st.expander("View underlying data"):
                            display = monthly_split.copy()
                            display['Total MT']     = total_per_month
                            display['Chicory Share %'] = norm['Chicory Blend'].round(2)
                            st.dataframe(display.style.format("{:,.1f}"), use_container_width=True)

                    # ── Download pooled analysis dataset ──────────────────
                    st.markdown("<br>", unsafe_allow_html=True)
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                        pooled.to_excel(writer, sheet_name='Pooled Data', index=False)
                    buf.seek(0)
                    st.download_button(
                        "⬇  Download pooled multi-file dataset",
                        data=buf.getvalue(),
                        file_name="MULTI_FILE_POOLED_ANALYSIS.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_pooled",
                    )
