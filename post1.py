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
    
    /* Secondary Action Button (Reset Fields) */
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #FF6C37 !important;
        border: 1px solid #FF6C37 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #FFF0EB !important;
        border-color: #E05626 !important;
        color: #E05626 !important;
    }
    
    /* Unified Look for Custom Banners */
    .metric-banner {
        padding: 12px !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        text-align: center !important;
    }
    
    /* Code Viewer Background Styling */
    div[data-testid="stCodeBlock"], pre {
        background-color: #F8F9FA !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("🚀 Postman-like API Client")
st.caption(
    "A lightweight REST API client built with Streamlit to test your endpoints."
)

# ----------------- TRUE STATE RESET LOGIC -----------------
# We use a state version key appended to element keys to force widgets to rebuild from blank
if "reset_token" not in st.session_state:
    st.session_state.reset_token = 0

if "clear_clicked" in st.session_state and st.session_state.clear_clicked:
    st.session_state.url_input = ""
    st.session_state.headers_json = ""
    st.session_state.body_json = "{}"
    st.session_state.text_body = ""
    st.session_state.param_keys = [""]
    st.session_state.param_vals = [""]
    st.session_state.auth_type_select = "No Auth"
    if "basic_user" in st.session_state: st.session_state.basic_user = ""
    if "basic_pass" in st.session_state: st.session_state.basic_pass = ""
    if "bearer_token" in st.session_state: st.session_state.bearer_token = ""
    st.session_state.reset_token += 1  # Increment to break widget cache
    st.session_state.clear_clicked = False  

# Fallback basic state initialization
if "url_input" not in st.session_state: st.session_state.url_input = ""
if "headers_json" not in st.session_state: st.session_state.headers_json = ""
if "body_json" not in st.session_state: st.session_state.body_json = "{}"
if "text_body" not in st.session_state: st.session_state.text_body = ""
if "param_keys" not in st.session_state: st.session_state.param_keys = [""]
if "param_vals" not in st.session_state: st.session_state.param_vals = [""]
if "auth_type_select" not in st.session_state: st.session_state.auth_type_select = "No Auth"

# Layout: Method, URL input, and Clean Reset button side-by-side
col1, col2, col3 = st.columns([1.2, 4.3, 1.1])

with col1:
    method = st.selectbox(
        "Method", ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        key=f"method_select_{st.session_state.reset_token}",
        label_visibility="collapsed"
    )

with col2:
    url = st.text_input(
        "Request URL", 
        placeholder="https://api.example.com/v1/resource",
        key="url_input",
        label_visibility="collapsed"
    )

with col3:
    if st.button("🔄 Reset Fields", use_container_width=True):
        st.session_state.clear_clicked = True
        st.rerun()

# Tabs for Request Configuration - Authorization is now ordered first
tab_auth, tab_params, tab_headers, tab_body = st.tabs(
    ["Authorization", "QueryParams", "Headers", "Body"]
)

# 1. Authorization Tab (Auth Type on Top Row, Credentials cleanly dropped below)
with tab_auth:
    st.markdown("##### Authentication")
    
    auth_headers = {}
    auth_tuple = None

    # Line 1: Type Selection
    a_row1_col1, _ = st.columns([2.5, 4.5])
    with a_row1_col1:
        auth_type = st.selectbox(
            "Auth Type", ["No Auth", "Bearer Token", "Basic Auth"],
            key="auth_type_select"
        )

    # Line 2: Drop active credentials context onto the next line layout
    if auth_type != "No Auth":
        st.write(" ") # Spacing gap
        a_row2_col1, a_row2_col2, _ = st.columns([2.5, 2.5, 2])
        
        if auth_type == "Bearer Token":
            with a_row2_col1:
                token = st.text_input("Token", type="password", placeholder="eyJhbGciOi...", key="bearer_token")
                if token:
                    auth_headers["Authorization"] = f"Bearer {token}"
                    
        elif auth_type == "Basic Auth":
            with a_row2_col1:
                username = st.text_input("Username", placeholder="Username", key="basic_user")
            with a_row2_col2:
                password = st.text_input("Password", type="password", placeholder="Password", key="basic_pass")
            if username or password:
                auth_tuple = (username, password)

# 2. Query Parameters Tab
with tab_params:
    st.markdown("##### Query Parameters")
    
    current_params = {}
    updated_keys = []
    updated_vals = []
    row_to_remove = None
    
    for i in range(len(st.session_state.param_keys)):
        p_col1, p_col2, p_col3 = st.columns([4, 4, 1])
        with p_col1:
            k = st.text_input(f"Key {i+1}", value=st.session_state.param_keys[i], key=f"p_key_{i}_{st.session_state.reset_token}", placeholder="key", label_visibility="collapsed")
        with p_col2:
            v = st.text_input(f"Value {i+1}", value=st.session_state.param_vals[i], key=f"p_val_{i}_{st.session_state.reset_token}", placeholder="value", label_visibility="collapsed")
        with p_col3:
            if st.button("🗑️", key=f"p_del_{i}_{st.session_state.reset_token}", help="Remove this row"):
                row_to_remove = i
        
        updated_keys.append(k)
        updated_vals.append(v)
        if k.strip():
            current_params[k.strip()] = v
            
    if row_to_remove is not None:
        updated_keys.pop(row_to_remove)
        updated_vals.pop(row_to_remove)
        st.session_state.param_keys = updated_keys
        st.session_state.param_vals = updated_vals
        st.rerun()
    else:
        st.session_state.param_keys = updated_keys
        st.session_state.param_vals = updated_vals

    if st.button("➕ Add Parameter Row"):
        st.session_state.param_keys.append("")
        st.session_state.param_vals.append("")
        st.rerun()

# 3. Headers Tab
with tab_headers:
    st.markdown("##### Request Headers")
    headers_input = st.text_area(
        "Enter JSON for custom headers",
        placeholder='Example: {"Content-Type": "application/json"}',
        key="headers_json",
        label_visibility="collapsed"
    )

# 4. Body Tab
with tab_body:
    st.markdown("##### Request Body")
    body_type = st.radio("Body Type", ["None", "JSON", "Text"], horizontal=True, key=f"body_type_{st.session_state.reset_token}")

    body_data = None
    if body_type == "JSON":
        body_input = st.text_area(
            "JSON Body", placeholder='Example: {"name": "John Doe"}', key="body_json", label_visibility="collapsed"
        )
    elif body_type == "Text":
        body_input = st.text_area("Raw Text Body", key="text_body", label_visibility="collapsed")
    else:
        body_input = None

st.write(" ")

# Send Request Button Layout
btn_col1, _ = st.columns([1.2, 4.8])
with btn_col1:
    send_clicked = st.button("Send Request", type="primary", use_container_width=True)

if send_clicked:
    if not url:
        st.error("Please enter a valid URL.")
    else:
        try:
            headers = json.loads(headers_input) if headers_input.strip() else {}
        except json.JSONDecodeError:
            st.error("Invalid JSON format in Headers.")
            st.stop()

        if auth_headers:
            headers.update(auth_headers)

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

        with st.spinner("Sending request..."):
            try:
                start_time = time.time()
                
                if body_type == "JSON":
                    response = requests.request(
                        method=method,
                        url=url,
                        params=current_params,
                        headers=headers,
                        json=payload,
                        auth=auth_tuple,
                        timeout=30
                    )
                else:
                    response = requests.request(
                        method=method,
                        url=url,
                        params=current_params,
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
                    st.warning(f"📦 Payload Size: {size_kb} KB")

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