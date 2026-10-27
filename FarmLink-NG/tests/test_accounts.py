import pytest
from farmlink.services.accounts import signup,authenticate
def test_signup_normalizes_email_and_authenticates(db):
    u=signup(db,name="Test Farmer",email=" FARMER@example.com ",password="strong-password-123",role="farmer")
    assert u.email=="farmer@example.com"
    assert authenticate(db,"FARMER@example.com","strong-password-123").id==u.id
def test_public_signup_cannot_create_admin(db):
    with pytest.raises(ValueError): signup(db,name="No Admin",email="noadmin@example.com",password="strong-password-123",role="admin")
def test_duplicate_email_rejected(db):
    signup(db,name="Test Farmer",email="farmer@example.com",password="strong-password-123",role="farmer")
    with pytest.raises(ValueError): signup(db,name="Another",email="FARMER@example.com",password="strong-password-123",role="buyer")
