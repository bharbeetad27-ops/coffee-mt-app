import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Coffee Trade Intelligence",
    layout="wide"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* Page background */
.stApp {
    background: linear-gradient(180deg, #020617 0%, #020617 100%);
    color: white;
    font-family: 'Inter', sans-serif;
}

/* Hero section */
.hero {
    background-image: linear-gradient(rgba(2,6,23,0.75), rgba(2,6,23,0.95)),
                      url("https://images.unsplash.com/photo-1498804103079-a6351b050096");
    background-size: cover;
    background-position: center;
    padding: 80px 40px;
    border-radius: 16px;
    margin-bottom: 40px;
}

.hero h1 {
    font-size: 42px;
    font-weight: 600;
    margin-bottom: 10px;
}

.hero p {
    color: #94a3b8;
    font-size: 16px;
}

/* Section container */
.section {
    background: #f8fafc;
    padding: 40px;
    border-radius: 16px;
    margin-bottom: 40px;
}

/* Feature grid */
.feature-grid {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.feature {
    position: relative;
    flex: 1;
    min-width: 250px;
    height: 200px;
    border-radius: 12px;
    overflow: hidden;
}

.feature img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.feature .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.85), rgba(0,0,0,0.2));
    display: flex;
    align-items: flex-end;
    padding: 20px;
}

.feature h3 {
    color: white;
    margin: 0;
    font-size: 18px;
}

.feature p {
    color: #cbd5f5;
    font-size: 13px;
}

/* Pipeline section */
.pipeline {
    padding: 20px;
}

.block {
    background: #0f172a;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.block h3 {
    color: white;
}

.stFileUploader {
    background: #020617 !important;
    border-radius: 10px;
}

/* Buttons */
.stButton button {
    background: #1d4ed8;
    color: white;
    border-radius: 8px;
}

/* Mobile */
@media (max-width: 768px) {
    .hero {
        padding: 40px 20px;
    }
    .hero h1 {
        font-size: 28px;
    }
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
    <div class="overlay">
        <div>
            <h3>High Volume Processing</h3>
            <p>Handle large export datasets efficiently</p>
        </div>
    </div>
</div>

<div class="feature">
    <img src="https://images.unsplash.com/photo-1509042239860-f550ce710b93">
    <div class="overlay">
        <div>
            <h3>Smart Classification</h3>
            <p>Coffee & Chicory separation using HSN codes</p>
        </div>
    </div>
</div>

<div class="feature">
    <img src="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085">
    <div class="overlay">
        <div>
            <h3>Accurate MT Conversion</h3>
            <p>Reliable conversion across formats</p>
        </div>
    </div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

# ---------------- PIPELINE ----------------
st.markdown('<div class="pipeline">', unsafe_allow_html=True)

st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("Stage 1 — Upload Exclusion List")
exclusion_file = st.file_uploader("Upload Excel file", type=["xlsx"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("Stage 2 — Upload Raw Data")
raw_files = st.file_uploader("Upload raw files", type=["xlsx"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RUN BUTTON ----------------
run = st.button("Run Pipeline")

# ---------------- CORE LOGIC ----------------
if run:
    st.success("Processing started...")

    # ⚠️ IMPORTANT
    # PASTE YOUR EXISTING CONVERSION LOGIC BELOW
    # (I DID NOT CHANGE YOUR LOGIC)

    # Example placeholder:
    if exclusion_file and raw_files:
        st.info("Files received successfully")
        
        # 👉 YOUR EXISTING CODE GOES HERE
        # ---------------------------------
        # df = process_data(...)
        # ---------------------------------

        st.success("Conversion completed")

        # Example metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows Processed", "12,540")
        col2.metric("Coffee Records", "8,320")
        col3.metric("Chicory Records", "4,220")

        st.download_button("Download Output", data="sample", file_name="output.xlsx")

    else:
        st.error("Please upload required files")

st.markdown('</div>', unsafe_allow_html=True)
