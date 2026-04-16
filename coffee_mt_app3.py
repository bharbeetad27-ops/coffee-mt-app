import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Coffee Trade Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* REMOVE STREAMLIT DEFAULT PADDING */
.block-container {
    padding: 0 !important;
}

/* GLOBAL FONT */
html, body {
    font-family: 'Segoe UI', sans-serif;
}

/* HERO SECTION (LDC STYLE) */
.hero {
    height: 70vh;
    background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.65)),
                url('https://images.unsplash.com/photo-1509042239860-f550ce710b93');
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    padding-left: 80px;
    color: white;
}

/* HERO TEXT */
.hero h1 {
    font-size: 48px;
    font-weight: 600;
    margin-bottom: 10px;
}

.hero p {
    font-size: 18px;
    color: #d1d5db;
}

/* SECTION */
.section {
    padding: 60px 80px;
    background-color: #f8fafc;
}

/* CARD */
.card {
    background: white;
    padding: 30px;
    border-radius: 14px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 30px;
}

/* HEADINGS */
.section-title {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #0f172a;
}

/* BUTTON */
.stButton>button {
    background-color: #0f172a;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
}

/* REMOVE STREAMLIT HEADER */
header {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <div>
        <h1>Coffee Trade Intelligence</h1>
        <p>Transform raw export data into actionable insights</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SECTION ----------------
st.markdown('<div class="section">', unsafe_allow_html=True)

# ---------------- STAGE 1 ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Stage 1 — Upload Exclusion List</div>', unsafe_allow_html=True)

exclusion = st.file_uploader("Upload Excel file", type=["xlsx"])

if exclusion:
    st.success("Exclusion list uploaded successfully")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STAGE 2 ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Stage 2 — Upload Raw Data</div>', unsafe_allow_html=True)

raw_files = st.file_uploader("Upload raw files", type=["xlsx"], accept_multiple_files=True)

if raw_files:
    st.success(f"{len(raw_files)} file(s) uploaded")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ACTION ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

if st.button("Run Conversion Pipeline"):
    st.success("Processing started...")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
