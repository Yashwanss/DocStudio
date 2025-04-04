import streamlit as st
import markdown
from pygments.formatters import HtmlFormatter
from PIL import Image
import imgkit
import pdfkit
import base64
import zipfile
import os
from io import BytesIO

# --- App Configuration ---
st.set_page_config(page_title="DocStudio by WIKI", layout="wide")
st.markdown("<style>body { font-family: 'Segoe UI', sans-serif; }</style>", unsafe_allow_html=True)

# # --- Password Protection ---
# PASSWORD = st.secrets.get("app_password", "docstudio123")  # fallback for local testing

# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# if not st.session_state.authenticated:
#     password_input = st.text_input("🔐 Enter password to access DocStudio:", type="password")
#     if password_input == PASSWORD:
#         st.session_state.authenticated = True
#         st.rerun()
#     else:
#         st.stop()

# --- Branding ---
st.title("📄 DocStudio by WIKI")

# --- Theme Selector ---
theme = st.sidebar.radio("🌗 Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #1e1e1e; color: white; }
        textarea, .stTextInput > div > div { background-color: #2e2e2e !important; color: white; }
        </style>
    """, unsafe_allow_html=True)

# --- Markdown Input & Upload ---
st.subheader("📥 Upload or Paste Markdown")
uploaded_file = st.file_uploader("Upload .md or image", type=["md", "markdown", "png", "jpg", "jpeg"])

if "markdown_text" not in st.session_state:
    st.session_state.markdown_text = ""

pasted_text = st.text_area("✍️ Paste Markdown below:", value=st.session_state.markdown_text, height=250)
st.session_state.markdown_text = pasted_text

markdown_content = ""

# Handle upload
if uploaded_file:
    if uploaded_file.name.endswith((".md", ".markdown")):
        markdown_content = uploaded_file.read().decode("utf-8")
        st.session_state.markdown_text = markdown_content
    elif uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

if st.session_state.markdown_text:
    markdown_content = st.session_state.markdown_text

# --- Render Markdown ---
if markdown_content:
    st.subheader("🔍 Live Preview")

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

    st.subheader("📤 Export Options")

    # --- Export: HTML ---
    st.download_button("⬇️ Download HTML", full_html, file_name="doc.html", mime="text/html")

    # --- Export: PDF ---
    try:
        pdf_bytes = pdfkit.from_string(full_html, False)
        st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name="doc.pdf", mime="application/pdf")
    except Exception as e:
        st.error("❌ PDF Export failed. Ensure wkhtmltopdf is installed.")

    # --- Export: Image ---
    try:
        image_bytes = imgkit.from_string(full_html, False, options={"format": "png"})
        b64_image = base64.b64encode(image_bytes).decode()
        st.markdown(f'<a href="data:image/png;base64,{b64_image}" download="doc.png">🖼️ Download PNG</a>', unsafe_allow_html=True)
    except Exception as e:
        st.warning("⚠️ Image export failed.")

    # --- Export: ZIP ---
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("doc.md", markdown_content)
        zip_file.writestr("doc.html", full_html)
        if 'pdf_bytes' in locals():
            zip_file.writestr("doc.pdf", pdf_bytes)
        if 'image_bytes' in locals():
            zip_file.writestr("doc.png", image_bytes)

    st.download_button("📦 Download All as ZIP", data=zip_buffer.getvalue(), file_name="docstudio_exports.zip", mime="application/zip")

else:
    st.info("Paste or upload Markdown to preview and export.")
