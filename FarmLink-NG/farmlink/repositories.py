from sqlalchemy import select,desc
from sqlalchemy.orm import joinedload
from farmlink.models import User,Product,AuditLog
def get_user_by_email(db,email): return db.scalar(select(User).where(User.email==email.strip().lower()))
def list_products(db,status="approved",category="",location="",search="",min_price=None,max_price=None,sort="newest",limit=100):
    q=select(Product).options(joinedload(Product.farmer)).where(Product.status==status,Product.is_available.is_(True))
    if category and category!="All": q=q.where(Product.category==category)
    if location: q=q.where(Product.location.ilike(f"%{location}%"))
    if search:
        term=f"%{search}%"; q=q.where(Product.title.ilike(term)|Product.description.ilike(term))
    if min_price is not None: q=q.where(Product.price >= min_price)
    if max_price is not None: q=q.where(Product.price <= max_price)
    ordering = Product.price.asc() if sort == "price_low" else Product.price.desc() if sort == "price_high" else desc(Product.created_at)
    return list(db.scalars(q.order_by(ordering).limit(limit)).unique())
def log_action(db,actor_id,action,target_type,target_id="",detail=""):
    db.add(AuditLog(actor_id=actor_id,action=action,target_type=target_type,target_id=str(target_id),detail=detail[:1000]))
