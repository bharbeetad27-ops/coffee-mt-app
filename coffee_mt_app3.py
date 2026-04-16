import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Coffee Trade Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* REMOVE DEFAULT PADDING */
.block-container {
    padding-left: 5rem;
    padding-right: 5rem;
    padding-top: 1rem;
}

/* PAGE BACKGROUND */
body {
    background-color: #f5f7fa;
}

/* HERO SECTION */
.hero {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    padding: 40px;
    border-radius: 16px;
    color: white;
    margin-bottom: 30px;
}

/* SECTION HEADINGS */
.section-title {
    font-size: 28px;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 10px;
    color: #0f172a;
}

/* UPLOAD BOX */
.upload-box {
    background: #1e293b;
    padding: 20px;
    border-radius: 12px;
}

/* SUCCESS BOX */
.success-box {
    background: #dcfce7;
    padding: 10px;
    border-radius: 8px;
    color: #166534;
    font-weight: 500;
}

/* BUTTON */
.stButton>button {
    background-color: #0f172a;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h2 style="margin-bottom:0;">☕ Coffee Trade Analytics</h2>
<p style="color:#64748b;">Trade Intelligence Tool</p>
""", unsafe_allow_html=True)

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero">
    <h1 style="margin-bottom:10px;">Trade Data Conversion Engine</h1>
    <p style="color:#cbd5f5;">Upload → Clean → Convert → Download</p>
</div>
""", unsafe_allow_html=True)

# ---------------- STAGE 1 ----------------
st.markdown('<div class="section-title">Stage 1 — Upload Exclusion List</div>', unsafe_allow_html=True)

uploaded_exclusion = st.file_uploader("Upload exclusion list", type=["xlsx"])

if uploaded_exclusion:
    st.markdown('<div class="success-box">✔ Exclusion list uploaded successfully</div>', unsafe_allow_html=True)

# ---------------- STAGE 2 ----------------
st.markdown('<div class="section-title">Stage 2 — Upload Raw Data Files</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload raw files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    st.markdown(f'<div class="success-box">✔ {len(uploaded_files)} file(s) uploaded</div>', unsafe_allow_html=True)

# ---------------- RUN BUTTON ----------------
if st.button("Run Pipeline"):
    st.success("Processing started... (logic will go here)")
