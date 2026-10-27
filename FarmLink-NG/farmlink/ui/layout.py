import streamlit as st
from farmlink.ui.styles import load
def setup():
    st.set_page_config(page_title="FarmLink NG",page_icon="🌱",layout="wide")
    load()
def sidebar():
    with st.sidebar:
        st.markdown("## 🌱 FarmLink NG"); st.caption("Connecting Farmers Directly to Buyers")
        st.page_link("app.py",label="Home",icon="🏡")
        st.page_link("pages/1_Marketplace.py",label="Marketplace",icon="🧺")
        st.page_link("pages/2_Account.py",label="Sign in / Create account",icon="👤")
        u=st.session_state.get("user")
        if u:
            st.divider(); st.caption(f"Signed in as **{u['name']}**")
            page={"farmer":"pages/3_Farmer_Dashboard.py","buyer":"pages/4_Buyer_Dashboard.py","admin":"pages/5_Admin.py"}.get(u["role"])
            if page: st.page_link(page,label=f"{u['role'].title()} dashboard")
            if st.button("Sign out",use_container_width=True): st.session_state.pop("user",None); st.rerun()
def footer():
    st.markdown('<div class="footer">© FarmLink NG · Connecting Farmers Directly to Buyers.<br>Purchase requests are coordination records; payment and delivery are arranged directly between parties.</div>',unsafe_allow_html=True)
def require_role(role):
    u=st.session_state.get("user")
    if not u or u.get("role")!=role:
        st.warning(f"Sign in with a {role} account to access this page."); st.page_link("pages/2_Account.py",label="Go to sign in"); st.stop()
    return u
