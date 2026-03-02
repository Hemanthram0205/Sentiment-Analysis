import streamlit as st
from auth import COMMON_CSS

st.set_page_config(
    page_title="Sign In — Sentiment Analyzer Pro",
    page_icon="📊",
    layout="centered",
)

st.markdown(COMMON_CSS, unsafe_allow_html=True)

# If already logged in, go straight to analyzer
if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Analyzer.py")

# ── Login UI ──────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:2rem">
  <div style="font-size:3rem">📊</div>
  <h1 style="font-size:2rem;font-weight:800;color:#4e54c8;margin:0.4rem 0">
    Sentiment Analyzer Pro
  </h1>
  <p style="color:#6b7280;margin:0">AI-powered sentiment & emotion analysis</p>
</div>
""", unsafe_allow_html=True)

# Card wrapper
st.markdown('<div class="card" style="max-width:400px;margin:0 auto">', unsafe_allow_html=True)

tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])

# ── Sign In ──────────────────────────────────────────────────
with tab_login:
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Email / Username", placeholder="demo")
        password = st.text_input("Password", type="password", placeholder="demo123")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

    if submitted:
        if not username or not password:
            st.error("Please fill in both fields.")
        else:
            # Load credentials from secrets (or fallback demo credentials)
            try:
                users = st.secrets["users"]
            except Exception:
                users = {"demo": "demo123", "admin": "admin123"}

            if username in users and users[username] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("✅ Login successful! Redirecting…")
                st.switch_page("pages/1_Analyzer.py")
            else:
                st.error("❌ Invalid username or password.")

    st.markdown("""
    <p style="font-size:0.82rem;color:#9ca3af;text-align:center;margin-top:0.5rem">
      Demo credentials: <code>demo</code> / <code>demo123</code>
    </p>
    """, unsafe_allow_html=True)

# ── Sign Up ───────────────────────────────────────────────────
with tab_signup:
    with st.form("signup_form", clear_on_submit=True):
        new_name  = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_pass  = st.text_input("Password (min 8 chars)", type="password")
        new_conf  = st.text_input("Confirm Password", type="password")
        reg_btn   = st.form_submit_button("Create Account", use_container_width=True, type="primary")

    if reg_btn:
        if not all([new_name, new_email, new_pass, new_conf]):
            st.error("All fields are required.")
        elif len(new_pass) < 8:
            st.error("Password must be at least 8 characters.")
        elif new_pass != new_conf:
            st.error("Passwords do not match.")
        else:
            # For Streamlit Cloud: user management requires a backend DB.
            # This demo auto-logs in after "registration".
            st.session_state["authenticated"] = True
            st.session_state["username"] = new_email.split("@")[0]
            st.success("✅ Account created! Redirecting…")
            st.switch_page("pages/1_Analyzer.py")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="footer">© 2026 Sentiment Analyzer Pro</div>',
    unsafe_allow_html=True
)
