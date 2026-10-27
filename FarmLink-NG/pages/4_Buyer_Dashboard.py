import streamlit as st
from sqlalchemy import select, desc
from farmlink.database import get_session
from farmlink.models import User, Enquiry, PurchaseRequest, Product
from farmlink.services.marketplace import cancel_purchase_request
from farmlink.ui.layout import setup, sidebar, footer, require_role

setup(); sidebar(); session_user = require_role("buyer"); st.title("Buyer dashboard")
with get_session() as db:
    actor = db.get(User, session_user["id"])
    if not actor or not actor.is_active:
        st.error("Account inactive. Contact an administrator."); st.stop()
    st.subheader("Purchase requests")
    requests = list(db.scalars(select(PurchaseRequest).where(PurchaseRequest.buyer_id == actor.id).order_by(desc(PurchaseRequest.created_at))))
    if not requests:
        st.info("No purchase requests yet.")
    for request in requests:
        product = db.get(Product, request.product_id)
        with st.container(border=True):
            st.markdown(f"**{product.title if product else 'Listing unavailable'}**")
            st.write(f"Quantity: {request.quantity:g} · Status: **{request.status.title()}**")
            if request.note:
                st.write(request.note)
            if request.status == "pending":
                if st.button("Cancel pending request", key=f"cancel_{request.id}"):
                    try:
                        cancel_purchase_request(db, actor, request.id)
                        st.success("Purchase request cancelled."); st.rerun()
                    except (ValueError, PermissionError) as exc:
                        st.error(str(exc))
    st.subheader("Enquiries")
    enquiries = list(db.scalars(select(Enquiry).where(Enquiry.buyer_id == actor.id).order_by(desc(Enquiry.created_at))))
    if not enquiries:
        st.info("No enquiries yet.")
    for enquiry in enquiries:
        product = db.get(Product, enquiry.product_id)
        with st.container(border=True):
            st.markdown(f"**{product.title if product else 'Listing unavailable'}**")
            st.caption(f"Status: {enquiry.status.title()}")
            st.write(enquiry.message)
footer()
