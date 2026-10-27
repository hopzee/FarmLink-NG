from pathlib import Path
import streamlit as st
def load(): st.markdown(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>",unsafe_allow_html=True)
