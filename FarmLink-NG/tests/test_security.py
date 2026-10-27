import pytest
from farmlink.security import hash_password,verify_password
def test_password_hash_and_verify():
    h=hash_password("correct horse battery staple")
    assert h!="correct horse battery staple"
    assert verify_password(h,"correct horse battery staple")
    assert not verify_password(h,"wrong password")
def test_short_password_rejected():
    with pytest.raises(ValueError): hash_password("short")
