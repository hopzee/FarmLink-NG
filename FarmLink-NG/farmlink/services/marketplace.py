from sqlalchemy import select,desc
from farmlink.models import Product,User,Enquiry,PurchaseRequest
from farmlink.repositories import list_products,log_action
CATEGORIES=["Grains & cereals", "Tubers & roots", "Vegetables", "Fruits", "Legumes & beans", "Livestock", "Poultry & eggs", "Fish & seafood", "Cash crops", "Processed products", "Other"]
LEGACY_CATEGORIES={"Grains", "Tubers", "Poultry", "Fish"}
VALID_CATEGORIES=set(CATEGORIES) | LEGACY_CATEGORIES
def as_dict(p):
    return {"id":p.id,"title":p.title,"category":p.category,"description":p.description,"price":p.price,"unit":p.unit,"quantity":p.quantity,"location":p.location,"image_path":p.image_path,"farmer_name":p.farmer.name if p.farmer else "Farmer","farmer_id":p.farmer_id}
def featured_products(limit=6):
    from farmlink.database import get_session
    with get_session() as db: return list_products(db,limit=limit)
def create_product(db,actor,*,title,category,description,price,unit,quantity,location,image_path=""):
    if actor.role!="farmer" or not actor.is_active: raise PermissionError("Only active farmers can create listings.")
    if not title.strip() or not location.strip() or float(price)<0 or float(quantity)<=0: raise ValueError("Enter title and location, non-negative price, and positive quantity.")
    if category not in VALID_CATEGORIES: raise ValueError("Choose a valid product category.")
    if len(title.strip()) > 140 or len(location.strip()) > 120 or len(unit.strip()) > 40: raise ValueError("Some listing fields are too long.")
    p=Product(farmer_id=actor.id,title=title.strip(),category=category,description=description.strip(),price=float(price),unit=unit.strip() or "per unit",quantity=float(quantity),location=location.strip(),image_path=image_path,status="pending")
    db.add(p); db.commit(); db.refresh(p); log_action(db,actor.id,"product_created","product",p.id,"status=pending"); db.commit(); return p
def farmer_products(db,farmer_id):
    return list(db.scalars(select(Product).where(Product.farmer_id==farmer_id).order_by(desc(Product.created_at))))
def approved_products(db,category="",location="",search="",min_price=None,max_price=None,sort="newest"): return list_products(db,category=category,location=location,search=search,min_price=min_price,max_price=max_price,sort=sort)
def send_enquiry(db,buyer,product_id,message):
    if buyer.role!="buyer" or not buyer.is_active: raise PermissionError("Only active buyers can enquire.")
    p=db.get(Product,product_id)
    if not p or p.status!="approved" or not p.is_available: raise ValueError("Listing is not available.")
    if p.farmer_id==buyer.id: raise ValueError("You cannot enquire about your own listing.")
    if not message.strip(): raise ValueError("Please write a message.")
    row=Enquiry(product_id=p.id,buyer_id=buyer.id,message=message.strip()[:3000]); db.add(row); db.commit(); db.refresh(row)
    log_action(db,buyer.id,"enquiry_created","enquiry",row.id); db.commit(); return row
def request_purchase(db,buyer,product_id,quantity,note=""):
    if buyer.role!="buyer" or not buyer.is_active: raise PermissionError("Only active buyers can submit requests.")
    p=db.get(Product,product_id)
    if not p or p.status!="approved" or not p.is_available: raise ValueError("Listing is not available.")
    if p.farmer_id==buyer.id: raise ValueError("You cannot request your own listing.")
    if quantity<=0 or quantity>p.quantity: raise ValueError("Quantity must be positive and within the listed quantity.")
    row=PurchaseRequest(product_id=p.id,buyer_id=buyer.id,quantity=quantity,note=note.strip()[:3000]); db.add(row); db.commit(); db.refresh(row)
    log_action(db,buyer.id,"purchase_request_created","purchase_request",row.id); db.commit(); return row

def update_product(db, actor, product_id, *, title, category, description, price, unit, quantity, location, is_available=True):
    """Update a farmer's own listing without allowing ownership changes."""
    if actor.role != "farmer" or not actor.is_active:
        raise PermissionError("Only active farmers can update listings.")
    product = db.get(Product, product_id)
    if not product or product.farmer_id != actor.id:
        raise PermissionError("You can only update your own listings.")
    if not title.strip() or not location.strip() or float(price) < 0 or float(quantity) <= 0:
        raise ValueError("Enter a title and location, a non-negative price, and a positive quantity.")
    if category not in VALID_CATEGORIES:
        raise ValueError("Choose a valid product category.")
    if len(title.strip()) > 140 or len(location.strip()) > 120 or len(unit.strip()) > 40:
        raise ValueError("Some listing fields are too long.")
    product.title = title.strip()[:140]
    product.category = category
    product.description = description.strip()[:5000]
    product.price = float(price)
    product.unit = unit.strip()[:40] or "per unit"
    product.quantity = float(quantity)
    product.location = location.strip()[:120]
    product.is_available = bool(is_available)
    # Any material edit returns a listing to moderation before it is shown publicly.
    product.status = "pending"
    db.commit()
    log_action(db, actor.id, "product_updated", "product", product.id, "returned to pending review")
    db.commit()
    return product


def remove_product(db, actor, product_id):
    """Soft-remove a listing so historic requests remain intact."""
    if actor.role != "farmer" or not actor.is_active:
        raise PermissionError("Only active farmers can remove listings.")
    product = db.get(Product, product_id)
    if not product or product.farmer_id != actor.id:
        raise PermissionError("You can only remove your own listings.")
    product.is_available = False
    product.status = "removed"
    db.commit()
    log_action(db, actor.id, "product_removed", "product", product.id)
    db.commit()
    return product


def update_purchase_request(db, actor, request_id, status):
    """Allow the listing's farmer to accept/reject a pending request."""
    if actor.role != "farmer" or not actor.is_active:
        raise PermissionError("Only active farmers can respond to purchase requests.")
    if status not in {"accepted", "rejected"}:
        raise ValueError("Invalid purchase-request status.")
    row = db.get(PurchaseRequest, request_id)
    product = db.get(Product, row.product_id) if row else None
    if not row or not product or product.farmer_id != actor.id:
        raise PermissionError("You can only respond to requests for your own listings.")
    if row.status != "pending":
        raise ValueError("Only pending requests can be updated.")
    row.status = status
    db.commit()
    log_action(db, actor.id, f"purchase_request_{status}", "purchase_request", row.id)
    db.commit()
    return row


def cancel_purchase_request(db, actor, request_id):
    """Buyers can cancel only their own pending requests."""
    if actor.role != "buyer" or not actor.is_active:
        raise PermissionError("Only active buyers can cancel purchase requests.")
    row = db.get(PurchaseRequest, request_id)
    if not row or row.buyer_id != actor.id:
        raise PermissionError("You can only cancel your own requests.")
    if row.status != "pending":
        raise ValueError("Only pending requests can be cancelled.")
    row.status = "cancelled"
    db.commit()
    log_action(db, actor.id, "purchase_request_cancelled", "purchase_request", row.id)
    db.commit()
    return row
