from farmlink.models import User
from farmlink.repositories import get_user_by_email,log_action
from farmlink.security import SignupInput,hash_password,verify_password
def signup(db,*,name,email,password,role,phone="",location=""):
    payload=SignupInput(name=name.strip(),email=email,password=password,role=role,phone=phone.strip(),location=location.strip())
    if payload.role not in {"farmer","buyer"}: raise ValueError("Choose Farmer or Buyer. Admin accounts are CLI-only.")
    normalized=str(payload.email).strip().lower()
    if get_user_by_email(db,normalized): raise ValueError("An account with that email already exists.")
    user=User(name=payload.name,email=normalized,password_hash=hash_password(password),role=role,phone=payload.phone,location=payload.location)
    try:
        db.add(user); db.commit(); db.refresh(user)
        log_action(db,user.id,"account_created","user",user.id,f"role={user.role}"); db.commit()
        return user
    except Exception: db.rollback(); raise
def authenticate(db,email,password):
    user=get_user_by_email(db,email)
    if not user or not user.is_active or not verify_password(user.password_hash,password): return None
    return user
def create_admin(db,name,email,password):
    payload=SignupInput(name=name.strip(),email=email,password=password,role="admin")
    name=payload.name
    email=str(payload.email).strip().lower()
    if get_user_by_email(db,email): raise ValueError("An account with that email already exists.")
    user=User(name=name.strip(),email=email,password_hash=hash_password(password),role="admin")
    db.add(user); db.commit(); db.refresh(user)
    log_action(db,user.id,"admin_created","user",user.id,"created via CLI"); db.commit()
    return user
