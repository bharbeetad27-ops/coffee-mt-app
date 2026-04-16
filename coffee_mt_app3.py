import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Coffee Trade Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* REMOVE ALL DEFAULT PADDING */
.block-container {
    padding: 0 !important;
}

/* BACKGROUND */
.main {
    background-color: #0b1220;
}

/* HERO */
.hero {
    height: 60vh;
    background: linear-gradient(rgba(10,15,30,0.7), rgba(10,15,30,0.9)),
                url('https://images.unsplash.com/photo-1509042239860-f550ce710b93');
    background-size: cover;
    display: flex;
    align-items: center;
    padding: 80px;
    color: white;
}

/* HERO TEXT */
.hero h1 {
    font-size: 48px;
    font-weight: 600;
}

.hero p {
    color: #94a3b8;
}

/* SECTION WRAPPER */
.section {
    padding: 60px 80px;
}

/* CARD */
.card {
    background: #111827;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    color: white;
}

/* TITLE */
.title {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 10px;
}

/* METRICS */
.metric {
    background: #1f2937;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

.metric h3 {
    margin: 0;
    font-size: 28px;
}

.metric p {
    margin: 0;
    color: #9ca3af;
}

/* BUTTON */
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}

/* HIDE STREAMLIT UI */
header {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <div>
        <h1>Coffee Trade Intelligence</h1>
        <p>Upload → Clean → Convert → Download</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SECTION ----------------
st.markdown('<div class="section">', unsafe_allow_html=True)

# ---------------- STAGE 1 ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">Stage 1 — Upload Exclusion List</div>', unsafe_allow_html=True)

exclusion = st.file_uploader("Upload Excel file", type=["xlsx"])

if exclusion:
    st.success("Exclusion list uploaded")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STAGE 2 ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">Stage 2 — Upload Raw Data</div>', unsafe_allow_html=True)

files = st.file_uploader("Upload raw files", type=["xlsx"], accept_multiple_files=True)

file_count = len(files) if files else 0

if files:
    st.success(f"{file_count} file(s) uploaded")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- METRICS ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">Conversion Metrics</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric">
        <h3>{file_count}</h3>
        <p>Files Uploaded</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric">
        <h3>--</h3>
        <p>Records Processed</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric">
        <h3>--</h3>
        <p>Output Generated</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RUN BUTTON ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

if st.button("Run Conversion Pipeline"):
    st.success("Processing started...")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
