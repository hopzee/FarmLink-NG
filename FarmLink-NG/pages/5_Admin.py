import streamlit as st
from farmlink.database import get_session
from farmlink.models import User
from farmlink.services.admin import require_admin,pending_products,all_users,moderate_product,set_user_active,audit_logs
from farmlink.ui.layout import setup,sidebar,footer,require_role
setup(); sidebar(); su=require_role("admin"); st.title("Administration")
with get_session() as db:
    actor=db.get(User,su["id"]); require_admin(actor); pending=pending_products(db); users=all_users(db)
    a,b,c=st.columns(3); a.metric("Pending listings",len(pending)); b.metric("Registered users",len(users)); c.metric("Active users",sum(u.is_active for u in users))
    tabs=st.tabs(["Listing moderation","User management","Audit log"])
    with tabs[0]:
        if not pending: st.success("No listings waiting for review.")
        for p in pending:
            with st.container(border=True):
                st.subheader(p.title); st.caption(f"{p.category} · {p.location} · Farmer ID {p.farmer_id}"); st.write(p.description); st.write(f"₦{p.price:,.2f}/{p.unit} · Quantity {p.quantity:g}")
                x,y=st.columns(2)
                if x.button("Approve",key=f"ap{p.id}",type="primary"): moderate_product(db,actor,p.id,"approved"); st.rerun()
                if y.button("Reject",key=f"re{p.id}"): moderate_product(db,actor,p.id,"rejected"); st.rerun()
    with tabs[1]:
        for u in users:
            with st.container(border=True):
                x,y,z=st.columns([3,1,1]); x.markdown(f"**{u.name}**  \n{u.email}  \nRole: {u.role.title()} · {u.location or '—'}"); y.write("Active" if u.is_active else "Suspended")
                if u.id==actor.id or u.role=="admin": z.caption("Administrator")
                elif u.is_active:
                    if z.button("Suspend",key=f"s{u.id}"): set_user_active(db,actor,u.id,False); st.rerun()
                else:
                    if z.button("Reactivate",key=f"r{u.id}"): set_user_active(db,actor,u.id,True); st.rerun()
    with tabs[2]:
        logs=audit_logs(db)
        if not logs: st.info("No audit events yet.")
        for log in logs: st.caption(f"{log.created_at} · actor={log.actor_id} · {log.action} · {log.target_type} #{log.target_id}")
footer()
