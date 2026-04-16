import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Coffee Trade Intelligence",
    layout="wide"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>

/* MOBILE RESPONSIVENESS */
@media (max-width: 768px) {
    .hero {
        padding: 60px 20px !important;
    }

    .hero h1 {
        font-size: 28px !important;
    }

    .section {
        margin: -30px 10px 30px 10px !important;
        padding: 30px 15px !important;
    }

    .card-container {
        flex-direction: column !important;
    }

    .card {
        width: 100% !important;
    }

    button {
        width: 100% !important;
    }
}

/* Background */
body {
    background-color: #0b1220;
}

/* HERO */
.hero {
    background: linear-gradient(rgba(2,6,23,0.85), rgba(2,6,23,0.9)),
                url("https://images.unsplash.com/photo-1509042239860-f550ce710b93");
    background-size: cover;
    background-position: center;
    padding: 100px 5%;
    color: white;
    border-radius: 0 0 20px 20px;
}

/* LIGHT SECTION */
.section {
    background: #f8fafc;
    padding: 60px 5%;
    margin: -50px 5% 40px 5%;
    border-radius: 16px;
}

/* TEXT */
.section h2 {
    color: #0f172a;
    text-align: center;
}

.section p {
    color: #475569;
    text-align: center;
}

/* CARDS */
.card-container {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 250px;
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.08);
}

.card h3 {
    color: #0f172a;
}

.card p {
    color: #64748b;
}

/* TOOL SECTION */
.tool {
    padding: 40px 5%;
    color: white;
}

/* METRICS */
.metric-box {
    background: #1e293b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.metric-box h3 {
    margin: 0;
    font-size: 28px;
}

.metric-box p {
    margin: 0;
    color: #94a3b8;
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
<p>
Automate classification, cleaning and MT conversion of export data in seconds
</p>

<div class="card-container">

<div class="card">
<h3>⚡ Fast Processing</h3>
<p>Upload raw files and instantly process large datasets.</p>
</div>

<div class="card">
<h3>📊 Smart Classification</h3>
<p>Automatically separates Coffee & Chicory using HS codes.</p>
</div>

<div class="card">
<h3>📦 Accurate Conversion</h3>
<p>Handles KGS, NOS, ML and complex formats reliably.</p>
</div>

</div>

</div>
""", unsafe_allow_html=True)

# ---------------- TOOL ----------------
st.markdown('<div class="tool">', unsafe_allow_html=True)

st.header("Data Processing Pipeline")

# Upload exclusion
st.subheader("Stage 1 — Upload Exclusion List")
exclusion_file = st.file_uploader("Upload exclusion Excel", type=["xlsx"])

# Upload raw files
st.subheader("Stage 2 — Upload Raw Data")
raw_files = st.file_uploader("Upload raw files", type=["xlsx"], accept_multiple_files=True)

# ---------------- PROCESS ----------------
if st.button("Run Conversion"):

    if raw_files:

        total_rows = 0
        total_weight = 0

        for file in raw_files:
            df = pd.read_excel(file)

            total_rows += len(df)

            if "NETWT" in df.columns:
                total_weight += df["NETWT"].sum()

        st.markdown("### Conversion Summary")

        col1, col2 = st.columns(2)

        col1.markdown(f"""
        <div class="metric-box">
            <h3>{total_rows}</h3>
            <p>Total Rows</p>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="metric-box">
            <h3>{round(total_weight,2)}</h3>
            <p>Total Weight (KGS)</p>
        </div>
        """, unsafe_allow_html=True)

        st.success("Processing Complete ✅")

    else:
        st.error("Please upload files")

st.markdown('</div>', unsafe_allow_html=True)
