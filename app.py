import streamlit as st
import json
import xml.dom.minidom as md
import datetime
import os
from urllib.parse import urljoin, urlparse
import tempfile
import zipfile
import io

st.set_page_config(page_title="Technical SEO Tool", page_icon="🔍")

def load_urls_from_file(uploaded_file):
    """Load URLs from an uploaded JSON file"""
    content = uploaded_file.getvalue().decode("utf-8")
    urls = json.loads(content)
    return urls

def generate_sitemap(urls, output_file="sitemap.xml"):
    """Generate sitemap.xml from a list of URLs"""
    
    doc = md.getDOMImplementation().createDocument(None, "urlset", None)
    root = doc.documentElement
    root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    
    for url in urls:
        url_element = doc.createElement("url")
        
        
        loc = doc.createElement("loc")
        loc_text = doc.createTextNode(url)
        loc.appendChild(loc_text)
        url_element.appendChild(loc)
        
        
        lastmod = doc.createElement("lastmod")
        lastmod_text = doc.createTextNode(today)
        lastmod.appendChild(lastmod_text)
        url_element.appendChild(lastmod)
        
        
        changefreq = doc.createElement("changefreq")
        changefreq_text = doc.createTextNode("weekly")
        changefreq.appendChild(changefreq_text)
        url_element.appendChild(changefreq)
        
        
        priority_value = "1.0" if url == urls[0] else "0.8"
        priority = doc.createElement("priority")
        priority_text = doc.createTextNode(priority_value)
        priority.appendChild(priority_text)
        url_element.appendChild(priority)
        
        
        root.appendChild(url_element)
    
    
    return doc.toprettyxml(indent="  ")

def generate_robots_txt(main_url, sitemap_filename="sitemap.xml"):
    """Generate robots.txt file with reference to sitemap"""
    base_url = f"{urlparse(main_url).scheme}://{urlparse(main_url).netloc}"
    sitemap_url = urljoin(base_url, sitemap_filename)
    
    content = f"""# robots.txt generated on {datetime.datetime.now().strftime("%Y-%m-%d")}
User-agent: *
Allow: /
# Disallow potential admin or private areas
Disallow: /admin/
Disallow: /private/
Disallow: /login/
Disallow: /wp-admin/
Disallow: /wp-login/
Disallow: /cart/
Disallow: /checkout/
Disallow: /auth/admin/
# Sitemap location
Sitemap: {sitemap_url}
"""
    return content

def create_zip_file(sitemap_content, robots_content):
    """Create a zip file containing sitemap.xml and robots.txt"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("sitemap.xml", sitemap_content)
        zipf.writestr("robots.txt", robots_content)
    
    zip_buffer.seek(0)
    return zip_buffer


st.title("Technical SEO Tool")
st.subheader("Generate Sitemap and Robots.txt")

with st.expander("How to Use", expanded=True):
    st.markdown("""
    1. Upload a JSON file containing an array of URLs
    2. The first URL in the array will be considered the main URL
    3. Download the generated sitemap.xml and robots.txt files
    
    *Example JSON format:*
    json
    [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/contact"
    ]
    
    """)


uploaded_file = st.file_uploader("Upload JSON file with URLs", type=["json"])


st.subheader("Or enter URLs manually")
manual_input = st.text_area("Enter URLs (one per line)")


if st.button("Generate Files"):
    if uploaded_file is not None:
        try:
            urls = load_urls_from_file(uploaded_file)
            st.success(f"Loaded {len(urls)} URLs from uploaded file")
        except Exception as e:
            st.error(f"Error loading JSON file: {e}")
            st.stop()
    elif manual_input:
        
        urls = [url.strip() for url in manual_input.split("\n") if url.strip()]
        if not urls:
            st.error("No valid URLs entered")
            st.stop()
        st.success(f"Loaded {len(urls)} URLs from manual input")
    else:
        st.error("Please upload a JSON file or enter URLs manually")
        st.stop()
    
    
    with st.expander("URLs to be included"):
        for i, url in enumerate(urls):
            st.text(f"{i+1}. {url}")
    
    
    main_url = urls[0]
    st.info(f"Main URL: {main_url}")
    
    
    sitemap_content = generate_sitemap(urls)
    
    
    robots_content = generate_robots_txt(main_url)
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("sitemap.xml")
        st.code(sitemap_content, language="xml")
        
    with col2:
        st.subheader("robots.txt")
        st.code(robots_content, language="text")
    
    
    zip_file = create_zip_file(sitemap_content, robots_content)
    st.download_button(
        label="Download Files (ZIP)",
        data=zip_file,
        file_name="seo_files.zip",
        mime="application/zip"
    )

st.divider()
st.caption("Technical SEO Tool for generating sitemap.xml and robots.txt files")