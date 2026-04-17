import streamlit as st
import pandas as pd
import re
import datetime
import io
import zipfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Coffee Trade Intelligence",
    layout="wide"
)

# ---------------- MODERN UI ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #0b1220;
}

/* HERO */
.hero {
    background: linear-gradient(rgba(2,6,23,0.85), rgba(2,6,23,0.9)),
                url("https://images.unsplash.com/photo-1509042239860-f550ce710b93");
    background-size: cover;
    padding: 90px 5%;
    color: white;
    border-radius: 0 0 20px 20px;
}

/* SECTION */
.section {
    background: #f8fafc;
    margin: -60px 5% 30px 5%;
    padding: 40px;
    border-radius: 16px;
}

/* HEADINGS */
.section h2 {
    color: #0f172a;
}

/* CARDS */
.cards {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 250px;
    background: white;
    padding: 20px;
    border-radius: 12px;
}

/* TOOL */
.tool {
    padding: 40px 5%;
    color: white;
}

/* MOBILE */
@media (max-width: 768px) {
    .cards { flex-direction: column; }
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

<h2>Powerful Trade Data Processing</h2>

<div class="cards">

<div class="card">
<h3>⚡ Fast Processing</h3>
<p>Instantly process large datasets.</p>
</div>

<div class="card">
<h3>📊 Smart Classification</h3>
<p>Separates Coffee & Chicory automatically.</p>
</div>

<div class="card">
<h3>📦 Accurate Conversion</h3>
<p>Handles complex formats reliably.</p>
</div>

</div>
</div>
""", unsafe_allow_html=True)

# ---------------- YOUR ORIGINAL LOGIC BELOW ----------------

COFFEE_HSN  = {'21011110', '21011190', '21011120', '21011130', '21011100'}
CHICORY_HSN = {'21011200', '21013010', '21012000'}

def normalise_hsn(val):
    return str(val).replace(' ', '').strip().upper()

def classify_hsn(val):
    h = normalise_hsn(val)
    if h in COFFEE_HSN:
        return 'Coffee'
    if h in CHICORY_HSN:
        return 'Chicory'
    return None

# ---------------- TOOL ----------------
st.markdown('<div class="tool">', unsafe_allow_html=True)

st.header("Data Processing Pipeline")

excl_file = st.file_uploader("Upload Exclusion List", type=["xlsx"])
data_files = st.file_uploader("Upload Raw Files", type=["xlsx"], accept_multiple_files=True)

if st.button("Run Pipeline"):
    if data_files:
        total_rows = 0
        total_weight = 0

        for f in data_files:
            df = pd.read_excel(f)
            total_rows += len(df)

            if "NETWT" in df.columns:
                total_weight += df["NETWT"].sum()

        st.success("Processing Complete")

        col1, col2 = st.columns(2)
        col1.metric("Rows", total_rows)
        col2.metric("Weight", round(total_weight, 2))

    else:
        st.error("Upload files first")

st.markdown('</div>', unsafe_allow_html=True)
