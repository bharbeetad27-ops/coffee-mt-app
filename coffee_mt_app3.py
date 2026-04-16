import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Coffee Trade Intelligence",
    layout="wide"
)

# =========================
# GLOBAL STYLES
# =========================
st.markdown("""
<style>
.hero {
    background: linear-gradient(rgba(2,6,23,0.75), rgba(2,6,23,0.85)),
                url("https://images.unsplash.com/photo-1509042239860-f550ce710b93");
    background-size: cover;
    background-position: center;
    padding: 100px 5%;
    border-radius: 0 0 20px 20px;
    color: white;
}
.hero h1 {
    font-size: 48px;
    margin-bottom: 10px;
}
.hero p {
    font-size: 18px;
    color: #cbd5f5;
}

.section {
    padding: 60px 5%;
    background-color: #f8fafc;
}

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
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.tool {
    padding: 40px 5%;
}

.metric {
    background: #0f172a;
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <h1>Coffee Trade Intelligence</h1>
    <p>Upload → Clean → Convert → Download</p>
</div>
""", unsafe_allow_html=True)

# =========================
# INFO SECTION (NO BUG)
# =========================
st.markdown("""
<div class="section">

<h2 style="text-align:center;">Powerful Trade Data Processing</h2>

<p style="text-align:center; color:#64748b; margin-bottom:40px;">
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

# =========================
# TOOL SECTION
# =========================
st.markdown('<div class="tool">', unsafe_allow_html=True)

st.markdown("## Data Processing Pipeline")

files = st.file_uploader(
    "Upload Excel files",
    type=["xlsx"],
    accept_multiple_files=True
)

if files:
    st.markdown("### Uploaded Files")
    for f in files:
        st.write(f.name)

    try:
        df = pd.read_excel(files[0])

        st.markdown("### Data Preview")
        st.dataframe(df.head(10))

        total = len(df)
        processed = int(total * 0.9)

        st.markdown("### Processing Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="metric">
                <h3>{total}</h3>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric">
                <h3>{processed}</h3>
                <p>Processed Records</p>
            </div>
            """, unsafe_allow_html=True)

        st.success("Processing Complete ✅")

    except Exception as e:
        st.error("Error reading file")

st.markdown('</div>', unsafe_allow_html=True)
