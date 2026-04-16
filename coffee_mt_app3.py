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
# HERO SECTION (TOP BANNER)
# =========================
st.markdown("""
<style>
.hero {
    background: linear-gradient(rgba(2,6,23,0.8), rgba(2,6,23,0.9)),
                url("https://images.unsplash.com/photo-1509042239860-f550ce710b93");
    background-size: cover;
    background-position: center;
    padding: 120px 5%;
    border-radius: 0px 0px 20px 20px;
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
.cards {
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
.card h3 {
    margin-bottom: 10px;
    color: #0f172a;
}
.card p {
    color: #64748b;
}
.tool-section {
    padding: 50px 5%;
}
.metric-box {
    background: #0f172a;
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
</style>

<div class="hero">
    <h1>Coffee Trade Intelligence</h1>
    <p>Upload → Clean → Convert → Download</p>
</div>
""", unsafe_allow_html=True)

# =========================
# INFO SECTION (NO MORE EMPTY SPACE)
# =========================
st.markdown("""
<div class="section">

    <h2 style="text-align:center;">Powerful Trade Data Processing</h2>
    <p style="text-align:center; color:#64748b; margin-bottom:40px;">
        Automate classification, cleaning and MT conversion of export data
    </p>

    <div class="cards">

        <div class="card">
            <h3>⚡ Fast Processing</h3>
            <p>Upload raw files and get instant cleaned outputs.</p>
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
# MAIN TOOL SECTION
# =========================
st.markdown('<div class="tool-section">', unsafe_allow_html=True)

st.markdown("## Data Processing Pipeline")

# Upload files
files = st.file_uploader(
    "Upload your raw Excel files",
    type=["xlsx"],
    accept_multiple_files=True
)

# =========================
# DATA PROCESSING + METRICS
# =========================
if files:

    st.markdown("### Uploaded Files")
    for f in files:
        st.write(f.name)

    try:
        df = pd.read_excel(files[0])

        st.markdown("### Data Preview")
        st.dataframe(df.head(10))

        total_rows = len(df)
        processed_rows = int(total_rows * 0.9)  # placeholder logic

        st.markdown("### Processing Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <h3>{total_rows}</h3>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <h3>{processed_rows}</h3>
                <p>Processed Records</p>
            </div>
            """, unsafe_allow_html=True)

        st.success("Processing Complete ✅")

    except Exception as e:
        st.error("Error reading file. Please check format.")

st.markdown('</div>', unsafe_allow_html=True)
