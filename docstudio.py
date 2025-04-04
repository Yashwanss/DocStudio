import streamlit as st
import markdown
from pygments.formatters import HtmlFormatter
from PIL import Image
import imgkit
import pdfkit
import zipfile
from io import BytesIO

# --- App Configuration ---
st.set_page_config(page_title="DocStudio by WIKI", layout="wide")
st.markdown("<style>body { font-family: 'Segoe UI', sans-serif; }</style>", unsafe_allow_html=True)

# --- 🎨 UI Improvements ---
st.markdown("""
    <style>
    .big-title { font-size: 2rem; font-weight: bold; }
    .sub-title { font-size: 1.2rem; color: #666; margin-bottom: 20px; }
    .upload-box { border: 2px dashed #bbb; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 🔹 Welcome Message ---
st.markdown("<h1 class='big-title'>📄 DocStudio by WIKI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Easily edit, preview, and export Markdown & images with syntax highlighting.</p>", unsafe_allow_html=True)

st.markdown("### 🌟 **What Can This App Do?**")
st.info("""
- 📄 **Write or upload Markdown files** (.md) to see a **live preview**.
- 🖼️ **Upload images** (PNG, JPG) to view them directly.
- 🎨 **Syntax highlighting** for code blocks.
- 🌗 **Switch between light & dark themes**.
- 📤 **Export your Markdown as**:
    - 📝 HTML file
    - 📄 PDF file
    - 🖼️ Image (PNG)
    - 📦 ZIP file (containing all exports)
""")

# --- 🌗 Theme Selector ---
theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #1e1e1e; color: white; }
        textarea, .stTextInput > div > div { background-color: #2e2e2e !important; color: white; }
        </style>
    """, unsafe_allow_html=True)

# --- 📥 Upload / Paste Markdown ---
st.markdown("### 📥 **Upload or Paste Markdown**")

uploaded_file = st.file_uploader("**Drag & drop a file (.md, .png, .jpg)**", type=["md", "markdown", "png", "jpg", "jpeg"])

if "markdown_text" not in st.session_state:
    st.session_state.markdown_text = ""

pasted_text = st.text_area("✍️ **Write or Paste Markdown Below:**", value=st.session_state.markdown_text, height=250)
st.session_state.markdown_text = pasted_text

markdown_content = ""

# Handle uploaded file
if uploaded_file:
    if uploaded_file.name.endswith((".md", ".markdown")):
        markdown_content = uploaded_file.read().decode("utf-8")
        st.session_state.markdown_text = markdown_content
    elif uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        st.image(image, caption="🖼️ Uploaded Image", use_column_width=True)

if st.session_state.markdown_text:
    markdown_content = st.session_state.markdown_text

# --- 🔍 Live Preview ---
if markdown_content:
    st.markdown("### 🔍 **Live Markdown Preview**")

    html_content = markdown.markdown(
        markdown_content,
        extensions=["fenced_code", "codehilite"]
    )

    code_css = HtmlFormatter(style="monokai").get_style_defs('.codehilite')
    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; padding: 20px; }}
            {code_css}
            pre {{ border-radius: 8px; padding: 12px; overflow-x: auto; }}
        </style>
    </head>
    <body>{html_content}</body>
    </html>
    """

    st.markdown(f"<style>{code_css}</style>", unsafe_allow_html=True)
    st.markdown(html_content, unsafe_allow_html=True)

    # --- 📤 Export Options ---
    st.markdown("### 📤 **Export Your Markdown**")
    st.markdown("Choose a format to download your document.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button("⬇️ Download HTML", full_html, file_name="doc.html", mime="text/html")

    try:
        pdf_bytes = pdfkit.from_string(full_html, False)
        with col2:
            st.download_button("📄 Download PDF", data=pdf_bytes, file_name="doc.pdf", mime="application/pdf")
    except:
        st.warning("⚠️ PDF export failed. Ensure wkhtmltopdf is installed.")

    try:
        image_bytes = imgkit.from_string(full_html, False, options={"format": "png"})
        with col3:
            st.download_button("🖼️ Download PNG", data=image_bytes, file_name="doc.png", mime="image/png")
    except:
        st.warning("⚠️ Image export failed.")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("doc.md", markdown_content)
        zip_file.writestr("doc.html", full_html)
        if 'pdf_bytes' in locals():
            zip_file.writestr("doc.pdf", pdf_bytes)
        if 'image_bytes' in locals():
            zip_file.writestr("doc.png", image_bytes)

    with col4:
        st.download_button("📦 Download All (ZIP)", data=zip_buffer.getvalue(), file_name="docstudio_exports.zip", mime="application/zip")

else:
    st.warning("⚠️ Paste or upload a Markdown file to see a preview and export.")
