import streamlit as st
from farmlink.database import get_session
from farmlink.services.accounts import signup,authenticate
from farmlink.ui.layout import setup,sidebar,footer
setup(); sidebar(); st.title("Your FarmLink account")
with st.expander("Sign in",expanded=True):
    with st.form("login"):
        email=st.text_input("Email"); password=st.text_input("Password",type="password"); submit=st.form_submit_button("Sign in",type="primary")
    if submit:
        with get_session() as db:
            u=authenticate(db,email,password)
            if u: st.session_state["user"]={"id":u.id,"name":u.name,"email":u.email,"role":u.role}; st.rerun()
            else: st.error("Email or password is incorrect, or account is inactive.")
with st.expander("Create account"):
    st.info("Administrator accounts are created through the command line, never public sign-up.")
    with st.form("register"):
        name=st.text_input("Full name"); email=st.text_input("Email address",key="newemail"); role=st.selectbox("Account type",["farmer","buyer"],format_func=lambda x:x.title()); phone=st.text_input("Phone (optional)"); location=st.text_input("Town / state"); pw=st.text_input("Password (10+ characters)",type="password"); confirm=st.text_input("Confirm password",type="password"); submit=st.form_submit_button("Create account",type="primary")
    if submit:
        if pw!=confirm: st.error("Passwords do not match.")
        else:
            try:
                with get_session() as db:
                    u=signup(db,name=name,email=email,password=pw,role=role,phone=phone,location=location); st.session_state["user"]={"id":u.id,"name":u.name,"email":u.email,"role":u.role}; st.rerun()
            except Exception as e: st.error(str(e))
footer()
