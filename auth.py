import streamlit as st

# ── Shared CSS (injected on every page) ──────────────────────
COMMON_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer, header { visibility: hidden; }

  .site-nav {
    background: linear-gradient(135deg, #4e54c8, #8f94fb);
    padding: 0.75rem 2rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    color: white;
  }
  .site-nav .logo { font-size: 1.3rem; font-weight: 800; }
  .site-nav .user  { font-size: 0.85rem; opacity: 0.85; }

  .page-hero {
    background: linear-gradient(135deg, #4e54c8, #8f94fb);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
  }
  .page-hero h1 { font-size: 2rem; font-weight: 800; margin: 0; }
  .page-hero p  { font-size: 1rem; opacity: 0.88; margin: 0.4rem 0 0; }

  .card {
    background: white;
    border: 1px solid #e0e0ef;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
  }
  .metric-card {
    background: white;
    border: 1px solid #e0e0ef;
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }
  .metric-label { font-size:0.72rem; font-weight:700; text-transform:uppercase;
                  letter-spacing:0.05em; color:#6b7280; margin-bottom:0.3rem; }
  .metric-value { font-size:2rem; font-weight:800; line-height:1.1; }
  .metric-sub   { font-size:0.78rem; color:#9ca3af; margin-top:0.25rem; }

  .positive { color: #2ed573; }
  .negative { color: #ff4757; }
  .neutral  { color: #9ca3af; }

  .result-box {
    background: #fafbff;
    border: 1px solid #e0e0ef;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.9rem;
  }
  .word-chip {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.2rem;
  }
  .chip-neg { background: rgba(255,71,87,0.12); color: #ff4757; }
  .chip-pos { background: rgba(46,213,115,0.12); color: #1a9e4e; }

  .emotion-bar-row { margin-bottom: 0.65rem; }
  .emotion-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    font-weight: 600;
    color: #374151;
  }
  .emotion-bar-track {
    height: 8px;
    background: #f0f0f5;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 0.25rem;
  }
  .emotion-tag {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.2rem 0.2rem 0.2rem 0;
  }
  .footer {
    text-align: center;
    color: #9ca3af;
    font-size: 0.83rem;
    margin-top: 3rem;
    padding: 1.5rem 0;
    border-top: 1px solid #f0f0f5;
  }
</style>
"""

# ── Auth Guard ────────────────────────────────────────────────
def require_auth():
    """Call at the top of every protected page. Stops page if not authenticated."""
    st.markdown(COMMON_CSS, unsafe_allow_html=True)
    if not st.session_state.get("authenticated"):
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem">
          <div style="font-size:3rem">🔐</div>
          <h2 style="color:#4e54c8;margin:0.5rem 0">Authentication Required</h2>
          <p style="color:#6b7280">Please sign in to access this page.</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("app.py", label="🔑 Go to Sign In")   # ← page_link, not switch_page
        st.stop()
    return True


def show_nav(current_page: str = ""):
    """Show top navigation bar with user info and logout button."""
    username = st.session_state.get("username", "User")
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"""
        <div class="site-nav">
          <span class="logo">📊 Sentiment Analyzer Pro</span>
          <span class="user">👤 {username}</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", key="logout_nav", use_container_width=True):
            st.session_state.clear()
            st.rerun()              # ← rerun instead of switch_page
