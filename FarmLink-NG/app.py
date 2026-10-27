import streamlit as st
from farmlink.database import init_db
from farmlink.ui.layout import setup, sidebar, footer
from farmlink.services.marketplace import featured_products, as_dict
from farmlink.ui.components import card
setup(); init_db(); sidebar()
st.markdown("""<section class="hero"><div class="eyebrow">FARMLINK NG · AGRICULTURAL MARKETPLACE</div><h1>Good food deserves<br><span>a better connection.</span></h1><p>Connect directly with Nigerian farmers and buyers. Discover fresh produce, ask questions, and make purchase requests without unnecessary middlemen.</p></section>""", unsafe_allow_html=True)
a,b,c=st.columns(3)
for col,icon,title,body in [(a,"🌱","For farmers","Showcase your harvest and reach more customers."),(b,"🧺","For buyers","Discover produce and connect with its source."),(c,"🤝","Direct connection","Discuss availability and arrange a purchase directly.")]:
    with col: st.markdown(f'<div class="feature"><div class="icon">{icon}</div><h3>{title}</h3><p>{body}</p></div>',unsafe_allow_html=True)
st.markdown('<div class="eyebrow">FROM THE MARKETPLACE</div><h2>Explore available produce</h2>',unsafe_allow_html=True)
products=featured_products(6)
if not products: st.info("The marketplace is ready for its first listings. Create a farmer account to add produce.")
else:
    cols=st.columns(3)
    for i,p in enumerate(products):
        with cols[i%3]: card(as_dict(p))
st.markdown("""<section class="how"><div class="eyebrow">SIMPLE BY DESIGN</div><h2>From harvest to handshake</h2><div class="steps"><div><b>01</b><h3>Discover</h3><p>Search by category, location, and availability.</p></div><div><b>02</b><h3>Connect</h3><p>Send an enquiry or purchase request.</p></div><div><b>03</b><h3>Agree directly</h3><p>Confirm quantity, delivery, and payment together.</p></div></div></section>""",unsafe_allow_html=True)
footer()
