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

# --- 🎨 UI Improvements ---
st.markdown("""
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .big-title { font-size: 2rem; font-weight: bold; color: #1E88E5; }
    .sub-title { font-size: 1.2rem; color: #555; margin-bottom: 20px; }
    .upload-box { border: 2px dashed #1E88E5; padding: 15px; border-radius: 10px; background-color: #f9f9f9; }
    .stButton>button { width: 100%; font-size: 16px; padding: 10px; background-color: #1E88E5; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #1565C0; }
    .stDownloadButton>button { background-color: #43A047; color: white; }
    .stDownloadButton>button:hover { background-color: #388E3C; }
    </style>
""", unsafe_allow_html=True)

# --- 🔹 Welcome Message ---
st.markdown("<h1 class='big-title'>📄 DocStudio by WIKI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Easily edit, preview, and export Markdown & images with high-quality exports.</p>", unsafe_allow_html=True)

st.markdown("### 🌟 **What Can This App Do?**")
st.info("""
- 📄 **Write or upload Markdown files** (.md) to see a **live preview**.
- 🖼️ **Upload images** (PNG, JPG) to view them directly.
- 🎨 **Syntax highlighting** for code blocks.
- 📤 **Export your Markdown as**:
    - 📝 HTML file
    - 📄 High-Quality PDF file
    - 🖼️ High-Quality Image (PNG)
    - 📦 ZIP file (containing all exports)
""")

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

    # --- High-Quality PDF Export ---
    try:
        pdf_options = {
            'page-size': 'A4',
            'dpi': 300,
            'disable-smart-shrinking': '',
            'enable-local-file-access': ''
        }
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdf_bytes = pdfkit.from_string(full_html, False, configuration=config)


        with col2:
            st.download_button("📄 Download High-Quality PDF", data=pdf_bytes, file_name="doc.pdf", mime="application/pdf")
    except Exception as e:
        st.warning(f"⚠️ PDF export failed: {e}")

    # --- High-Quality Image Export ---
    # --- High-Quality Image Export (Using Selenium) ---
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from PIL import Image
    from io import BytesIO

    # Set up headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200x800")

    driver = webdriver.Chrome(options=options)
    driver.get(f"data:text/html;charset=utf-8,{full_html}")

    # Take a screenshot
    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    # Convert to image
    image = Image.open(BytesIO(screenshot))

    # Save image as BytesIO
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")
    image_bytes = image_buffer.getvalue()

    with col3:
        st.download_button("🖼️ Download High-Quality PNG", data=image_bytes, file_name="doc.png", mime="image/png")
except Exception as e:
    st.warning(f"⚠️ Image export failed: {e}")

    full_html = ""  # Ensure it's always defined

if markdown_content:
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

# Ensure full_html exists before using it in ZIP
if full_html.strip():
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("doc.md", markdown_content)
        zip_file.writestr("doc.html", full_html)
        if 'pdf_bytes' in locals():
            zip_file.writestr("doc.pdf", pdf_bytes)
        if 'image_bytes' in locals():
            zip_file.writestr("doc.png", image_bytes)

    st.download_button("📦 Download All (ZIP)", data=zip_buffer.getvalue(), file_name="docstudio_exports.zip", mime="application/zip")
else:
    st.warning("⚠️ No valid content to export. Please enter Markdown first.")


    # --- ZIP File Download ---
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
