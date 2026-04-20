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
.feature p { color: #cbd5f5; font-size: 13px; }
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
# CONSTANTS — all HS codes stored as zero-padded 8-char STRINGS
# ================================================================
# Root cause of the original bug: Excel stores HS codes as floats
# (21011130.0) or strips leading zeros ("9019090"). Comparing those
# against a list of Python ints with isin() fails silently.
# Solution: normalise everything to 8-char strings at load time.

COFFEE_CODES = [
    '21011110',
    '21011120',
    '21011130',   # was silently dropped in previous version
    '21011190',
    '21011200',
]

CHICORY_CODES = [
    '21013010',
    '21013090',   # was previously '210130' (6-digit, never matched)
]

# Candidate pool — HS codes known to contain misclassified soluble
# coffee or chicory products. Included in the initial pull so
# description-level logic can decide what to keep.
CANDIDATE_CODES = [
    '09019090',  # "other coffee" residue — chukku kappi, ginger coffee granules
    '09019020',  # roasted/other coffee — BRU, chukku kappi, ginger coffee
    '09019010',  # coffee husks — palat ginger coffee, pavan chukke kappi
    '09012190',  # roasted coffee — filter/ground coffee powders (kaapi, cothas)
    '09012290',  # decaffeinated roasted — coffee powder
    '09011119',  # other arabica — coffee powder mixed with raw grades
    '09011129',  # arabica cherry A — coffee powder bottles mixed with beans
    '21039040',  # condiments — nellara wayanadan coffee, chukku kappi
    '09101190',  # spice extracts — rajam chukku coffee powder
    '09101290',  # ginger extracts — chukku mix, rajam sukku coffee
    '09109929',  # mixed spices — chukku malli kappi
    '09109100',  # curry/spice mixes — vijay ginger coffee chukku kappi
    '09024030',  # tea — nadan chukkukappi, ginger coffee
    '21012090',  # tea extracts — amazon coffee premix, instant coffee premix
    '21069099',  # misc food — rajam sukku coffee, bimah karupatti coffee premix
]

ALL_CODES = COFFEE_CODES + CHICORY_CODES + CANDIDATE_CODES

STRICT_COFFEE_CHECK_CODES = ['21011190', '21011200']

COFFEE_SIGNALS = [
    'COFFEE', 'KAPPI', 'CAPPI', 'COFFE', 'COFEE',
    'CAPPUCCINO', 'CAPUCCINO', 'CAPUCHINO',
    'CPC', 'LATTE', 'ESPRESSO', 'AMERICANO', 'MOCHA',
    'MACCHIATO', 'FRAPPE', 'COLD BREW', 'COLD COFFEE',
    'NESCAFE', 'NESCAFE', 'BRU', 'LEVISTA', 'DAVIDOFF',
    'COTHAS', 'CONTINENTAL', 'CHAIZUP',
    'TATA COFFEE', 'CAFE', 'CAFE',
    'SPRAY DRIED', 'FREEZE DRIED', 'AGGLOMERATED',
    'DECOCTION', 'PERCOLATE', 'ROAST AND GROUND', 'CHICORY',
    'KAAPI', 'KAPI',
]

WEAK_COFFEE_SIGNALS = [
    'PREMIX', 'PRE-MIX', '3 IN 1', '2 IN 1',
    'SACHET', 'MIX', 'VENDING MIX',
]

TEA_SIGNALS = [
    'TEA', 'GREEN TEA', 'BLACK TEA',
    'MASALA TEA', 'CHAI', 'LEMON TEA', 'ICED TEA',
]

CHICORY_SIGNALS = [
    'CHUKKU', 'CHICORY', 'CHICOREE', 'SUKKU', 'CHIKKU',
    'KAPPI', 'KAAPI', 'GINGER COFFEE', 'NELLARA', 'WAYANADAN',
    'CHUKKE', 'CHUKKUKAPPI', 'CHUKKU KAPPI', 'SUKKU KAPPI',
    'ADU KAPPI', 'NADAN KAPPI',
]

RAW_BEAN_SIGNALS = [
    'NOT ROASTED', 'GREEN BEAN', 'GREEN COFFEE BEAN', 'PARCHMENT',
    'CHERRY AB', 'CHERRY A ', 'CHERRY-A', 'CHERRY-AB',
    'PLANTATION A', 'PLANTATION B', 'ARABICA WASHED',
    'ROBUSTA CHERRY', 'GREEN COFFE', 'MONSOONED',
    'ICO MARK', 'EUDR', 'JUTE BAG', 'BULK BAG',
    'WASHED ARABICA', 'WASHED COFFEE ARABICA',
]

STOP_WORDS = ['WITH MAGGI', 'FRW', 'EACH', 'PR FRAPPE']

# ================================================================
# HELPER: normalise any HS code value to zero-padded 8-char string
# ================================================================
def normalise_hs(val):
    """
    Converts any HS code representation to a zero-padded 8-character string.
      int    9019090   -> '09019090'
      float  21011130.0 -> '21011130'
      str    '21011120' -> '21011120'
      str    '9019090'  -> '09019090'
    """
    try:
        s = str(val).strip()
        if '.' in s:
            s = s.split('.')[0]
        s = re.sub(r'\D', '', s)   # strip any non-digit characters
        return s.zfill(8)
    except Exception:
        return ''


# ================================================================
# EXCLUSION LOGIC
# ================================================================
def should_exclude(desc, hs_norm, excl_df):
    """
    Returns (exclude: bool, reason: str).
    hs_norm is a zero-padded 8-char string (e.g. '21011190').
    """
    desc = str(desc).upper()

    # ── CHICORY CODES: never exclude if any chicory signal present ──
    # Previously products like "NELLARA CHUKKU KAPPI" under 21013090
    # had no "CHICORY" keyword so fell through to the exclusion list
    # and were incorrectly dropped.
    if hs_norm in CHICORY_CODES:
        if any(s in desc for s in CHICORY_SIGNALS):
            return False, ''
        return False, 'CHICORY CODE — VERIFY DESCRIPTION'

    # ── STRICT COFFEE SIGNAL CHECK ──
    if hs_norm in STRICT_COFFEE_CHECK_CODES:
        strong = any(s in desc for s in COFFEE_SIGNALS)
        weak   = any(s in desc for s in WEAK_COFFEE_SIGNALS)
        tea    = any(s in desc for s in TEA_SIGNALS)
        if strong:
            return False, ''
        elif tea:
            return True, 'Tea detected'
        elif weak:
            return False, 'Premix assumed coffee'
        else:
            return True, 'No coffee signal'

    # ── GENERAL EXCLUSION LIST ──
    for _, r in excl_df.iterrows():
        if r['MATCH_TYPE'] == 'CONTAINS' and r['KEYWORD'] in desc:
            return True, r['REASON']

    return False, ''


# ================================================================
# CANDIDATE POOL CLASSIFIER
# ================================================================
def classify_candidate(desc):
    """
    Classifies a product from CANDIDATE_CODES into COFFEE / CHICORY / EXCLUDE
    based purely on its description.
    """
    desc = str(desc).upper()

    # Hard exclude: raw green beans that tripped coffee keywords
    if any(r in desc for r in RAW_BEAN_SIGNALS):
        return 'EXCLUDE'

    # Non-coffee items that sometimes appear alongside coffee
    non_coffee = [
        'COFFEE SYRUP', 'COFFEE CREAMER', 'COFFEE RUSH', 'PROTEIN BAR',
        'NON DAIRY CREAMER', 'COFFEE HUSK', 'COFFEE FRAPPE POWDER',
        'NALANGU MAYU', 'ICED TEA', 'LEMON TEA', 'PEACH ICED TEA',
    ]
    if any(nc in desc for nc in non_coffee):
        return 'EXCLUDE'

    # Tea premixes that mention coffee only incidentally
    if 'TEA PREMIX' in desc and 'COFFEE FLAVOUR' in desc:
        return 'EXCLUDE'

    # Chicory / chukku signals
    if any(s in desc for s in CHICORY_SIGNALS):
        return 'CHICORY'

    # Strong coffee signals
    if any(s in desc for s in COFFEE_SIGNALS):
        return 'COFFEE'

    return 'EXCLUDE'


# ================================================================
# MT CONVERSION
# ================================================================
def convert_to_mt(row):
    qty  = row.get('STANDARD QUANTITY')
    unit = str(row.get('STANDARD QUANTITY UNIT', '')).upper()
    desc = str(row.get('PRODUCT DESCRIPTION', '')).upper()

    if pd.isna(qty):
        return None, 'BLANK'
    try:
        qty = float(qty)
    except (ValueError, TypeError):
        return None, 'BLANK'

    # ---------------- DIRECT ----------------
    if unit in ('KGS', 'KG'):
        return qty / 1000, 'DIRECT'
    if unit in ('MTS', 'MT'):
        return qty, 'DIRECT'
    if unit in ('ML', 'MLT', 'LTR'):
        return qty / 1_000_000, 'DIRECT'

    # ---------------- PARSING ----------------
    if unit in ('NOS', 'PCS', 'CTM', 'CTN'):
        try:
            clean = desc
            for sw in STOP_WORDS:
                if sw in clean:
                    clean = clean.split(sw)[0]
            clean = clean.replace(' X ', 'X').replace('*', 'X')

            m = re.search(r'(\d+)\((\d+)X(\d+(?:\.\d+)?)G\)', clean)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) * float(m.group(3)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)KG', clean)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)KGX(\d+)', clean)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1000, 'PARSED'

            m = re.search(r'(\d+)X(\d+(?:\.\d+)?)G', clean)
            if m:
                return qty * float(m.group(1)) * float(m.group(2)) / 1_000_000, 'PARSED'

            m = re.search(r'(\d+)X(\d+)(?![A-Z])', clean)
            if m:
                val2 = float(m.group(2))
                if val2 < 2000:
                    return qty * float(m.group(1)) * val2 / 1_000_000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*KGS?\s*NET', clean)
            if m:
                return qty * float(m.group(1)) / 1000, 'PARSED'

            m = re.search(r'(\d+(?:\.\d+)?)\s*GRM', clean)
            if m:
                return qty * float(m.group(1)) / 1_000_000, 'PARSED'

            grams = re.findall(r'(\d+(?:\.\d+)?)\s*G', clean)
            if grams:
                return qty * float(grams[-1]) / 1_000_000, 'PARSED'

            kg = re.findall(r'(\d+(?:\.\d+)?)\s*KG', clean)
            if kg:
                return qty * float(kg[-1]) / 1000, 'PARSED'

            ml = re.findall(r'(\d+(?:\.\d+)?)\s*ML', clean)
            if ml:
                return qty * float(ml[-1]) / 1_000_000, 'PARSED'

        except Exception:
            return None, 'BLANK'

    return None, 'BLANK'


# ================================================================
# FILE LOADERS
# ================================================================
@st.cache_data
def load_exclusion_list(file):
    return pd.read_excel(file)


@st.cache_data
def load_raw_file(file):
    return pd.read_excel(file)


# ================================================================
# CORE PROCESSING
# ================================================================
def process_file(file, excl_df):
    df = load_raw_file(file)

    # Find HS code column
    hs_col = next((c for c in df.columns if 'HS' in c.upper()), None)
    if hs_col is None:
        st.error("Could not find an HS/HSN column in the uploaded file.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # ── CRITICAL: normalise HS column to zero-padded 8-char strings ──
    # This is why 21011130 and leading-zero codes were silently dropped:
    # pd.to_numeric turns '09019090' into 9019090 (int) or 9019090.0 (float),
    # and isin([int_list]) then silently mismatches. String normalisation fixes all cases.
    df['_hs_norm'] = df[hs_col].apply(normalise_hs)

    # Show diagnostic info so you can verify matching immediately
    all_unique   = sorted(df['_hs_norm'].unique().tolist())
    codes_matched = [c for c in all_unique if c in ALL_CODES]
    st.info(
        f"**{file.name}** — {len(df):,} total rows | "
        f"HS codes matched into pipeline: `{'`, `'.join(codes_matched) if codes_matched else 'NONE — check column name'}`"
    )

    # Filter to relevant codes using normalised column
    df = df[df['_hs_norm'].isin(ALL_CODES)].copy()

    # Split: primary (definitively correct codes) vs candidate (misclassification pool)
    primary_mask   = df['_hs_norm'].isin(COFFEE_CODES + CHICORY_CODES)
    candidate_mask = df['_hs_norm'].isin(CANDIDATE_CODES)

    primary_df   = df[primary_mask].copy()
    candidate_df = df[candidate_mask].copy()

    # ── Exclusion logic on primary rows (pass normalised HS string) ──
    results = primary_df.apply(
        lambda r: should_exclude(r['PRODUCT DESCRIPTION'], r['_hs_norm'], excl_df), axis=1
    )
    primary_df['_excl']   = [x[0] for x in results]
    primary_df['_reason'] = [x[1] for x in results]

    removed_primary = primary_df[primary_df['_excl']].copy()
    removed_primary['REASON'] = removed_primary['_reason']
    keep_primary = primary_df[~primary_df['_excl']].copy()

    # Clean internal columns
    for col in ['_excl', '_reason']:
        removed_primary.drop(columns=[col], inplace=True, errors='ignore')

    # Split kept primary into Coffee / Chicory using normalised column (still present)
    coffee  = keep_primary[keep_primary['_hs_norm'].isin(COFFEE_CODES)].copy()
    chicory = keep_primary[keep_primary['_hs_norm'].isin(CHICORY_CODES)].copy()
    removed = removed_primary.copy()

    # Drop _hs_norm from outputs
    for d in [coffee, chicory, removed]:
        d.drop(columns=['_hs_norm'], inplace=True, errors='ignore')

    # ── Classify candidate pool by description ──
    if not candidate_df.empty:
        candidate_df = candidate_df.copy()
        candidate_df['_class'] = candidate_df['PRODUCT DESCRIPTION'].apply(classify_candidate)

        extra_coffee   = candidate_df[candidate_df['_class'] == 'COFFEE'].copy()
        extra_chicory  = candidate_df[candidate_df['_class'] == 'CHICORY'].copy()
        extra_excluded = candidate_df[candidate_df['_class'] == 'EXCLUDE'].copy()

        extra_excluded['REASON'] = 'Candidate pool — no coffee/chicory signal in description'

        for d in [extra_coffee, extra_chicory, extra_excluded]:
            d.drop(columns=['_class', '_hs_norm'], inplace=True, errors='ignore')

        coffee  = pd.concat([coffee,  extra_coffee],   ignore_index=True)
        chicory = pd.concat([chicory, extra_chicory],  ignore_index=True)
        removed = pd.concat([removed, extra_excluded], ignore_index=True)

    # ── MT conversion ──
    for d in [coffee, chicory]:
        if len(d):
            mt_results  = d.apply(convert_to_mt, axis=1)
            d['MT']     = [x[0] for x in mt_results]
            d['STATUS'] = [x[1] for x in mt_results]

    return coffee, chicory, removed


# ================================================================
# EXCEL STYLING
# ================================================================
def apply_header_colours(buf):
    buf.seek(0)
    wb = load_workbook(buf)

    blue_fill  = PatternFill('solid', fgColor='1D4ED8')
    green_fill = PatternFill('solid', fgColor='15803D')
    white_font = Font(color='FFFFFF', bold=True)
    center     = Alignment(horizontal='center')

    if 'Coffee' in wb.sheetnames:
        for cell in wb['Coffee'][1]:
            cell.fill      = blue_fill
            cell.font      = white_font
            cell.alignment = center

    if 'Chicory' in wb.sheetnames:
        for cell in wb['Chicory'][1]:
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
                    c.to_excel(w,  sheet_name='Coffee',   index=False)
                    ch.to_excel(w, sheet_name='Chicory',  index=False)
                    e.to_excel(w,  sheet_name='Excluded', index=False)

                final_buf = apply_header_colours(buf)

                st.success(
                    f"✅ {f.name} — "
                    f"{len(c):,} coffee rows | "
                    f"{len(ch):,} chicory rows | "
                    f"{len(e):,} excluded"
                )
                st.download_button(
                    label=f"⬇ Download MT_CLEANED_{f.name}",
                    data=final_buf,
                    file_name=f"MT_CLEANED_{f.name}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

st.markdown('</div>', unsafe_allow_html=True)
