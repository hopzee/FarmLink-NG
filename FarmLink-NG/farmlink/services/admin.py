from sqlalchemy import select,desc
from farmlink.models import Product,User,AuditLog
from farmlink.repositories import log_action
def require_admin(actor):
    if not actor or actor.role!="admin" or not actor.is_active: raise PermissionError("Administrator access required.")
def moderate_product(db,actor,product_id,status):
    require_admin(actor)
    if status not in {"approved","rejected"}: raise ValueError("Invalid moderation status.")
    p=db.get(Product,product_id)
    if not p: raise ValueError("Listing not found.")
    p.status=status; log_action(db,actor.id,f"product_{status}","product",p.id); db.commit(); return p
def set_user_active(db,actor,user_id,active):
    require_admin(actor); u=db.get(User,user_id)
    if not u: raise ValueError("User not found.")
    if u.id==actor.id and not active: raise ValueError("You cannot suspend your own account.")
    u.is_active=bool(active); log_action(db,actor.id,"user_activated" if active else "user_suspended","user",u.id); db.commit(); return u
def pending_products(db): return list(db.scalars(select(Product).where(Product.status=="pending").order_by(desc(Product.created_at))))
def all_users(db): return list(db.scalars(select(User).order_by(desc(User.created_at))))
def audit_logs(db,limit=200): return list(db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)))
