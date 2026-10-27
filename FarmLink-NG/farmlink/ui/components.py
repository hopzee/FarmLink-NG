from pathlib import Path
import streamlit as st
def card(p):
    st.markdown('<div class="product">',unsafe_allow_html=True)
    path=p.get("image_path","")
    if path and Path(path).exists(): st.image(path,use_container_width=True)
    else: st.markdown('<div style="height:115px;background:#EAF4EC;display:flex;align-items:center;justify-content:center;font-size:3rem">🌾</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="body"><span class="pill">{p.get("category","Produce")}</span><h3>{p.get("title","Produce")}</h3><div class="price">₦{p.get("price",0):,.2f} <span style="font-size:.8rem;font-weight:500;color:#667085">/ {p.get("unit","unit")}</span></div><p>📍 {p.get("location","Nigeria")}<br>👨🏽‍🌾 {p.get("farmer_name","Farmer")}<br>Available: {p.get("quantity",0):g} {p.get("unit","units")}</p></div></div>',unsafe_allow_html=True)
