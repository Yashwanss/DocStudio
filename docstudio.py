import streamlit as st
import markdown
from pygments.formatters import HtmlFormatter
from PIL import Image
import pdfkit
import zipfile
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- App Configuration ---
st.set_page_config(page_title="DocStudio by WIKI", layout="wide")

# --- 🎨 UI Improvements ---
st.markdown("""
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .big-title { font-size: 2rem; font-weight: bold; color: #1E88E5; }
    .sub-title { font-size: 1.2rem; color: #555; margin-bottom: 20px; }
    .stButton>button { width: 100%; font-size: 16px; padding: 10px; background-color: #1E88E5; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #1565C0; }
    .stDownloadButton>button { background-color: #43A047; color: white; }
    .stDownloadButton>button:hover { background-color: #388E3C; }
    </style>
""", unsafe_allow_html=True)

# --- 🔹 Welcome Message ---
st.markdown("<h1 class='big-title'>📄 DocStudio by WIKI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Easily edit, preview, and export Markdown & images with high-quality exports.</p>", unsafe_allow_html=True)

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

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.download_button("⬇️ Download HTML", full_html, file_name="doc.html", mime="text/html")

    # --- High-Quality PDF Export ---
    try:
        pdf_options = {
            'page-size': 'A4',
            'dpi': 300,
            'disable-smart-shrinking': '',
            'enable-local-file-access': ''
        }
        pdf_bytes = pdfkit.from_string(full_html, False, options=pdf_options)

        with col2:
            st.download_button("📄 Download High-Quality PDF", data=pdf_bytes, file_name="doc.pdf", mime="application/pdf")
    except Exception as e:
        st.warning(f"⚠️ PDF export failed: {e}")

    # --- Image Export Using Selenium ---
    def export_image(html):
        """Generates a PNG image of the rendered HTML using Selenium."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1200x800")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(f"data:text/html;charset=utf-8,{html}")

        screenshot = driver.get_screenshot_as_png()
        driver.quit()

        image = Image.open(BytesIO(screenshot))
        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")

        return image_buffer.getvalue()

    with col3:
        if st.button("🖼️ Download as Image"):
            image_data = export_image(full_html)
            st.download_button("🖼️ Download PNG", data=image_data, file_name="export.png", mime="image/png")

    # --- ZIP File Download ---
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("doc.md", markdown_content)
        zip_file.writestr("doc.html", full_html)
        if 'pdf_bytes' in locals():
            zip_file.writestr("doc.pdf", pdf_bytes)

    with col4:
        st.download_button("📦 Download All (ZIP)", data=zip_buffer.getvalue(), file_name="docstudio_exports.zip", mime="application/zip")

else:
    st.warning("⚠️ Paste or upload a Markdown file to see a preview and export.")
