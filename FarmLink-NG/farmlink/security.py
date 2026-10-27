from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError,InvalidHashError
from pydantic import BaseModel,EmailStr,Field
_hasher=PasswordHasher()
def hash_password(password):
    if len(password)<10: raise ValueError("Password must be at least 10 characters.")
    return _hasher.hash(password)
def verify_password(encoded,password):
    try: return _hasher.verify(encoded,password)
    except (VerifyMismatchError,InvalidHashError,TypeError): return False
class SignupInput(BaseModel):
    name:str=Field(min_length=2,max_length=120)
    email:EmailStr
    password:str=Field(min_length=10,max_length=128)
    role:str
    phone:str=Field(default="",max_length=40)
    location:str=Field(default="",max_length=120)
