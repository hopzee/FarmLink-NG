import streamlit as st
from farmlink.database import get_session
from farmlink.ui.layout import setup,sidebar,footer
from farmlink.services.marketplace import approved_products,CATEGORIES,as_dict,send_enquiry,request_purchase
from farmlink.ui.components import card
from farmlink.models import User
setup(); sidebar(); st.title("Marketplace"); st.write("Find produce from farmers across Nigeria.")
a,b,c=st.columns([1,1,2]); category=a.selectbox("Category",["All"]+CATEGORIES); location=b.text_input("Location",placeholder="e.g. Osun"); search=c.text_input("Search produce")
d,e,f=st.columns(3)
min_price=d.number_input("Minimum price (₦)",min_value=0.0,value=0.0,step=100.0)
max_price=e.number_input("Maximum price (₦, 0 = no limit)",min_value=0.0,value=0.0,step=100.0)
sort_label=f.selectbox("Sort by",["Newest first","Price: low to high","Price: high to low"])
sort_key={"Newest first":"newest","Price: low to high":"price_low","Price: high to low":"price_high"}[sort_label]
with get_session() as db:
    products=approved_products(db,category,location,search,min_price=min_price,max_price=max_price if max_price > 0 else None,sort=sort_key)
    if not products: st.info("No approved listings match these filters yet.")
    else:
        cols=st.columns(3)
        for i,p in enumerate(products):
            with cols[i%3]:
                card(as_dict(p))
                with st.expander("Details & contact"):
                    st.write(p.description or "No additional description.")
                    u=st.session_state.get("user")
                    if u and u["role"]=="buyer":
                        with st.form(f"enq{p.id}"):
                            msg=st.text_area("Message to farmer")
                            if st.form_submit_button("Send enquiry"):
                                try: send_enquiry(db,db.get(User,u["id"]),p.id,msg); st.success("Enquiry sent.")
                                except Exception as e: st.error(str(e))
                        with st.form(f"buy{p.id}"):
                            qty=st.number_input("Quantity",min_value=.1,max_value=max(.1,float(p.quantity)),value=min(1.,max(.1,float(p.quantity))),key=f"qty{p.id}")
                            note=st.text_input("Optional note",key=f"note{p.id}")
                            if st.form_submit_button("Request purchase"):
                                try: request_purchase(db,db.get(User,u["id"]),p.id,qty,note); st.success("Request sent. No payment was taken.")
                                except Exception as e: st.error(str(e))
                    elif not u: st.caption("Sign in as a buyer to enquire or request a purchase.")
footer()
