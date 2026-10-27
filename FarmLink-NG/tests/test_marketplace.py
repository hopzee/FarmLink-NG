import pytest
from farmlink.services.accounts import signup,create_admin
from farmlink.services.marketplace import create_product,request_purchase,send_enquiry
from farmlink.services.admin import moderate_product
def user(db,name,email,role): return signup(db,name=name,email=email,password="strong-password-123",role=role)
def test_listing_requires_approval_then_purchase_request(db):
    farmer=user(db,"Farmer","farmer@example.com","farmer"); buyer=user(db,"Buyer","buyer@example.com","buyer")
    p=create_product(db,farmer,title="Yam",category="Tubers",description="Fresh",price=500,unit="tuber",quantity=10,location="Ede, Osun")
    with pytest.raises(ValueError): request_purchase(db,buyer,p.id,1,"")
    admin=create_admin(db,"Admin","admin@example.com","strong-password-123"); moderate_product(db,admin,p.id,"approved")
    assert request_purchase(db,buyer,p.id,2,"Call first").quantity==2
def test_cannot_enquire_about_own_listing(db):
    farmer=user(db,"Farmer","farmer@example.com","farmer"); admin=create_admin(db,"Admin","admin@example.com","strong-password-123")
    p=create_product(db,farmer,title="Rice",category="Grains",description="",price=1000,unit="bag",quantity=4,location="Osogbo")
    moderate_product(db,admin,p.id,"approved")
    with pytest.raises(PermissionError): send_enquiry(db,farmer,p.id,"Interested")

def test_farmer_can_accept_own_purchase_request(db):
    from farmlink.services.marketplace import update_purchase_request
    farmer = user(db, "Farmer", "farmer2@example.com", "farmer")
    buyer = user(db, "Buyer", "buyer2@example.com", "buyer")
    admin = create_admin(db, "Admin", "admin2@example.com", "strong-password-123")
    product = create_product(db, farmer, title="Maize", category="Grains & cereals", description="", price=900, unit="bag", quantity=10, location="Ede")
    moderate_product(db, admin, product.id, "approved")
    request = request_purchase(db, buyer, product.id, 2, "Please call")
    assert update_purchase_request(db, farmer, request.id, "accepted").status == "accepted"


def test_buyer_can_cancel_only_own_pending_request(db):
    from farmlink.services.marketplace import cancel_purchase_request
    farmer = user(db, "Farmer", "farmer3@example.com", "farmer")
    buyer = user(db, "Buyer", "buyer3@example.com", "buyer")
    admin = create_admin(db, "Admin", "admin3@example.com", "strong-password-123")
    product = create_product(db, farmer, title="Yam", category="Tubers & roots", description="", price=600, unit="tuber", quantity=10, location="Ede")
    moderate_product(db, admin, product.id, "approved")
    request = request_purchase(db, buyer, product.id, 1, "")
    assert cancel_purchase_request(db, buyer, request.id).status == "cancelled"


def test_farmer_cannot_edit_another_farmers_listing(db):
    from farmlink.services.marketplace import update_product
    farmer = user(db, "Farmer", "farmer4@example.com", "farmer")
    other = user(db, "Other Farmer", "farmer5@example.com", "farmer")
    product = create_product(db, farmer, title="Beans", category="Legumes & beans", description="", price=1000, unit="bag", quantity=4, location="Osogbo")
    with pytest.raises(PermissionError):
        update_product(db, other, product.id, title="Changed", category="Other", description="", price=1, unit="bag", quantity=1, location="Osogbo")
