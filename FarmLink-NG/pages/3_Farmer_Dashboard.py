import streamlit as st
from sqlalchemy import select, desc
from farmlink.database import get_session
from farmlink.models import User, Product, PurchaseRequest
from farmlink.services.marketplace import (
    CATEGORIES, create_product, farmer_products, update_product,
    remove_product, update_purchase_request,
)
from farmlink.storage.images import save_product_image
from farmlink.ui.layout import setup, sidebar, footer, require_role

setup(); sidebar(); session_user = require_role("farmer"); st.title("Farmer dashboard")
with get_session() as db:
    actor = db.get(User, session_user["id"])
    if not actor or not actor.is_active:
        st.error("Account inactive. Contact an administrator."); st.stop()

    with st.expander("＋ Add a produce listing", expanded=False):
        with st.form("new_product"):
            title = st.text_input("Produce name")
            category = st.selectbox("Category", CATEGORIES)
            description = st.text_area("Description")
            a, b, c = st.columns(3)
            price = a.number_input("Price (₦)", min_value=0.0, step=100.0)
            unit = b.text_input("Unit", value="per bag")
            quantity = c.number_input("Available quantity", min_value=0.1, value=1.0, step=1.0)
            location = st.text_input("Pickup location", value=actor.location or "")
            image = st.file_uploader("Image (JPEG/PNG/WebP, max 5 MB)", type=["jpg", "jpeg", "png", "webp"])
            submit = st.form_submit_button("Submit for review", type="primary")
        if submit:
            try:
                image_path = save_product_image(image) if image else ""
                create_product(db, actor, title=title, category=category, description=description,
                               price=price, unit=unit, quantity=quantity, location=location, image_path=image_path)
                st.success("Submitted for administrator approval."); st.rerun()
            except (ValueError, PermissionError) as exc:
                st.error(str(exc))

    st.subheader("Your listings")
    products = farmer_products(db, actor.id)
    if not products:
        st.info("You have not listed produce yet.")
    for product in products:
        with st.container(border=True):
            st.subheader(product.title)
            st.caption(f"{product.category} · {product.location} · ₦{product.price:,.2f}/{product.unit}")
            st.write(f"Quantity: {product.quantity:g} · Status: **{product.status.title()}** · {'Available' if product.is_available else 'Unavailable'}")
            with st.expander("Edit listing"):
                with st.form(f"edit_{product.id}"):
                    new_title = st.text_input("Produce name", value=product.title, key=f"title_{product.id}")
                    options = CATEGORIES
                    category_index = options.index(product.category) if product.category in options else 0
                    new_category = st.selectbox("Category", options, index=category_index, key=f"cat_{product.id}")
                    new_description = st.text_area("Description", value=product.description or "", key=f"desc_{product.id}")
                    a, b, c = st.columns(3)
                    new_price = a.number_input("Price (₦)", min_value=0.0, value=float(product.price), step=100.0, key=f"price_{product.id}")
                    new_unit = b.text_input("Unit", value=product.unit, key=f"unit_{product.id}")
                    new_quantity = c.number_input("Quantity", min_value=0.1, value=float(product.quantity), step=1.0, key=f"quantity_{product.id}")
                    new_location = st.text_input("Pickup location", value=product.location, key=f"location_{product.id}")
                    available = st.checkbox("Available to buyers", value=product.is_available, key=f"available_{product.id}")
                    save = st.form_submit_button("Save changes and resubmit for review")
                if save:
                    try:
                        update_product(db, actor, product.id, title=new_title, category=new_category,
                                       description=new_description, price=new_price, unit=new_unit,
                                       quantity=new_quantity, location=new_location, is_available=available)
                        st.success("Changes saved. The listing is pending administrator review."); st.rerun()
                    except (ValueError, PermissionError) as exc:
                        st.error(str(exc))
            if product.status != "removed":
                if st.button("Remove listing", key=f"remove_{product.id}"):
                    remove_product(db, actor, product.id)
                    st.success("Listing removed from the public marketplace."); st.rerun()

    st.divider()
    st.subheader("Incoming purchase requests")
    requests = list(db.scalars(
        select(PurchaseRequest).join(Product, PurchaseRequest.product_id == Product.id)
        .where(Product.farmer_id == actor.id).order_by(desc(PurchaseRequest.created_at))
    ))
    if not requests:
        st.info("No purchase requests for your listings yet.")
    for request in requests:
        product = db.get(Product, request.product_id)
        buyer = db.get(User, request.buyer_id)
        with st.container(border=True):
            st.markdown(f"**{product.title if product else 'Listing unavailable'}** · {request.quantity:g} {product.unit if product else ''}")
            st.write(f"Buyer: {buyer.name if buyer else 'Unknown buyer'} · Status: **{request.status.title()}**")
            if request.note:
                st.write(request.note)
            if request.status == "pending":
                accept_col, reject_col = st.columns(2)
                if accept_col.button("Accept request", key=f"accept_{request.id}", type="primary"):
                    update_purchase_request(db, actor, request.id, "accepted"); st.rerun()
                if reject_col.button("Reject request", key=f"reject_{request.id}"):
                    update_purchase_request(db, actor, request.id, "rejected"); st.rerun()
footer()
