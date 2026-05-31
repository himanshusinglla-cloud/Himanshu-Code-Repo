import json
import time
import streamlit as st
import requests

# Set page configuration
st.set_page_config(
    page_title="Postman Clone", page_icon="🚀", layout="wide"
)

# ----------------- PROFESSIONAL POSTMAN STYLING (LIGHT ORANGE THEME) -----------------
st.markdown("""
<style>
    /* Main Background & Font Styling */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1C1E21 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Headers and Text Colors */
    h1, h2, h3, h4, h5, h6, .stMarkdown p {
        color: #1C1E21 !important;
    }
    .stCaption {
        color: #6B7280 !important;
    }
    
    /* Inputs: text inputs, dropdowns, textareas */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"], textarea {
        background-color: #F8F9FA !important;
        border: 1px solid #E4E7EB !important;
        border-radius: 6px !important;
        color: #1C1E21 !important;
    }
    
    /* Active/Focused Input Borders */
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #FF6C37 !important; /* Postman Orange */
        box-shadow: 0 0 0 1px #FF6C37 !important;
    }
    
    /* Tabs Component Styling */
    button[data-baseweb="tab"] {
        color: #6B7280 !important;
        background-color: transparent !important;
        border: none !important;
        font-weight: 500 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FF6C37 !important;
        border-bottom: 2px solid #FF6C37 !important;
    }
    
    /* Primary Action Button (Send Request) */
    div.stButton > button[kind="primary"] {
        background-color: #FF6C37 !important; /* Postman Accent Color */
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        transition: background 0.2s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #E05626 !important;
    }
    
    /* Secondary Action Button (Reset) */
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #1C1E21 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 4px !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #F3F4F6 !important;
        border-color: #FF6C37 !important;
    }
    
    /* Metrics / Cards Blocks Container styling */
    div[data-testid="stMetric"] {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        padding: 15px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    /* Code Viewer Background Styling */
    div[data-testid="stCodeBlock"], pre {
        background-color: #F8F9FA !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("🚀 API Client to Test REST API")
st.caption(
    "A lightweight REST API client built with Streamlit to test your endpoints."
)

# Sample headers shown as default guide text
DEFAULT_HEADERS_GUIDE = '{\n  "Content-Type": "application/json",\n  "Accept": "application/json",\n  "User-Agent": "Streamlit-Postman-Client"\n}'

# ----------------- REFRESH / CLEAR LOGIC -----------------
if "clear_clicked" in st.session_state and st.session_state.clear_clicked:
    st.session_state.url_input = ""
    st.session_state.params_json = "{}"
    st.session_state.headers_json = DEFAULT_HEADERS_GUIDE
    st.session_state.body_json = "{}"
    st.session_state.text_body = ""
    st.session_state.clear_clicked = False  

if "url_input" not in st.session_state:
    st.session_state.url_input = ""
if "params_json" not in st.session_state:
    st.session_state.params_json = "{}"
if "headers_json" not in st.session_state:
    st.session_state.headers_json = DEFAULT_HEADERS_GUIDE
if "body_json" not in st.session_state:
    st.session_state.body_json = "{}"
if "text_body" not in st.session_state:
    st.session_state.text_body = ""

# Layout: Method, URL input, and Clear button side-by-side
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    method = st.selectbox(
        "Method", ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    )

with col2:
    url = st.text_input(
        "Request URL", 
        placeholder="https://api.example.com/v1/resource",
        key="url_input"
    )

with col3:
    st.write(" ")  
    st.write(" ") 
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.clear_clicked = True
        st.rerun()

# Tabs for Request Configuration
tab_params, tab_auth, tab_headers, tab_body = st.tabs(
    ["QueryParams", "Authorization", "Headers", "Body"]
)

# 1. Query Parameters Tab
with tab_params:
    st.markdown("##### Query Parameters")
    params_input = st.text_area(
        "Enter JSON for query parameters",
        help='Example: {"limit": 10, "page": 1}',
        key="params_json",
    )

# 2. Authorization Tab
with tab_auth:
    st.markdown("##### Authentication")
    auth_type = st.selectbox("Auth Type", ["No Auth", "Bearer Token", "Basic Auth"])

    auth_headers = {}
    auth_tuple = None

    if auth_type == "Bearer Token":
        token = st.text_input("Token", type="password", placeholder="eyJhbGciOi...")
        if token:
            auth_headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "Basic Auth":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if username or password:
            auth_tuple = (username, password)

# 3. Headers Tab
with tab_headers:
    st.markdown("##### Request Headers")
    headers_input = st.text_area(
        "Enter JSON for custom headers",
        help='Example: {"Content-Type": "application/json"}',
        key="headers_json"
    )

# 4. Body Tab
with tab_body:
    st.markdown("##### Request Body")
    body_type = st.radio("Body Type", ["None", "JSON", "Text"], horizontal=True)

    body_data = None
    if body_type == "JSON":
        body_input = st.text_area(
            "JSON Body", help='Example: {"name": "John Doe"}', key="body_json"
        )
    elif body_type == "Text":
        body_input = st.text_area("Raw Text Body", key="text_body")
    else:
        body_input = None

# Send Request Button Layout
btn_col1, btn_col2 = st.columns([1, 4])
with btn_col1:
    send_clicked = st.button("Send Request", type="primary", use_container_width=True)

if send_clicked:
    if not url:
        st.error("Please enter a valid URL.")
    else:
        final_headers_input = "" if headers_input == DEFAULT_HEADERS_GUIDE else headers_input
        
        # 1. Safely Parse Query Params JSON
        try:
            params = json.loads(params_input) if params_input.strip() else {}
        except json.JSONDecodeError:
            st.error("Invalid JSON format in Query Parameters.")
            st.stop()

        # 2. Safely Parse Headers JSON
        try:
            headers = json.loads(final_headers_input) if final_headers_input.strip() else {}
        except json.JSONDecodeError:
            st.error("Invalid JSON format in Headers.")
            st.stop()

        if auth_headers:
            headers.update(auth_headers)

        # 3. Safely Parse Request Body JSON
        payload = None
        if body_type == "JSON" and body_input:
            try:
                payload = json.loads(body_input)
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
            except json.JSONDecodeError:
                st.error("Invalid JSON format in Request Body.")
                st.stop()
        elif body_type == "Text" and body_input:
            payload = body_input

        # 4. Execute Request
        with st.spinner("Sending request..."):
            try:
                start_time = time.time()
                
                if body_type == "JSON":
                    response = requests.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers,
                        json=payload,
                        auth=auth_tuple,
                        timeout=30
                    )
                else:
                    response = requests.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers,
                        data=payload,
                        auth=auth_tuple,
                        timeout=30
                    )

                end_time = time.time()
                elapsed_time = round((end_time - start_time) * 1000, 2)

                # --- OUTPUT SECTION ---
                st.subheader("Response")

                # Metrics banner
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    if 200 <= response.status_code < 300:
                        st.success(f"Status: {response.status_code} OK")
                    else:
                        st.error(f"Status: {response.status_code}")
                with m_col2:
                    st.info(f"⏱️ Time: {elapsed_time} ms")
                with m_col3:
                    size_kb = round(len(response.content) / 1024, 2)
                    st.metric(label="Payload Size", value=f"{size_kb} KB")

                # Response content views
                out_tab_body, out_tab_headers = st.tabs(["Response Body", "Response Headers"])
                
                is_json = False
                with out_tab_body:
                    try:
                        json_res = response.json()
                        st.json(json_res)
                        is_json = True
                    except ValueError:
                        if response.text:
                            st.code(response.text, language="text")
                        else:
                            st.info("No response body returned.")
                            
                with out_tab_headers:
                    st.json(dict(response.headers))

                # --- DOWNLOAD OPTION ---
                if response.text:
                    st.markdown("---")
                    file_ext = "json" if is_json else "txt"
                    mime_type = "application/json" if is_json else "text/plain"
                    
                    st.download_button(
                        label=f"📥 Download Response Body (.{file_ext})",
                        data=response.text,
                        file_name=f"response_{int(time.time())}.{file_ext}",
                        mime=mime_type,
                    )

            except requests.exceptions.MissingSchema:
                st.error("Invalid URL. Make sure it includes http:// or https://")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the server. Check the URL or your network.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")