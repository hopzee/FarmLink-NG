from datetime import datetime, timezone
from sqlalchemy import String,Integer,DateTime,Boolean,ForeignKey,Text,Float,Index
from sqlalchemy.orm import Mapped,mapped_column,relationship
from farmlink.database import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(120),nullable=False)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True,nullable=False)
    password_hash:Mapped[str]=mapped_column(String(255),nullable=False)
    role:Mapped[str]=mapped_column(String(20),nullable=False,default="buyer")
    phone:Mapped[str]=mapped_column(String(40),default="")
    location:Mapped[str]=mapped_column(String(120),default="")
    bio:Mapped[str]=mapped_column(Text,default="")
    is_active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    products:Mapped[list["Product"]]=relationship(back_populates="farmer")
class Product(Base):
    __tablename__="products"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    farmer_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False,index=True)
    title:Mapped[str]=mapped_column(String(140),nullable=False)
    category:Mapped[str]=mapped_column(String(60),nullable=False)
    description:Mapped[str]=mapped_column(Text,default="")
    price:Mapped[float]=mapped_column(Float,nullable=False)
    unit:Mapped[str]=mapped_column(String(40),default="per unit")
    quantity:Mapped[float]=mapped_column(Float,nullable=False,default=1)
    location:Mapped[str]=mapped_column(String(120),nullable=False)
    image_path:Mapped[str]=mapped_column(String(500),default="")
    status:Mapped[str]=mapped_column(String(20),default="pending",nullable=False)
    is_available:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    farmer:Mapped["User"]=relationship(back_populates="products")
    __table_args__=(Index("ix_products_status_category","status","category"),)
class Enquiry(Base):
    __tablename__="enquiries"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    product_id:Mapped[int]=mapped_column(ForeignKey("products.id"),nullable=False)
    buyer_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False)
    message:Mapped[str]=mapped_column(Text,nullable=False)
    status:Mapped[str]=mapped_column(String(20),default="open",nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class PurchaseRequest(Base):
    __tablename__="purchase_requests"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    product_id:Mapped[int]=mapped_column(ForeignKey("products.id"),nullable=False)
    buyer_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False)
    quantity:Mapped[float]=mapped_column(Float,nullable=False)
    note:Mapped[str]=mapped_column(Text,default="")
    status:Mapped[str]=mapped_column(String(20),default="pending",nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class AuditLog(Base):
    __tablename__="audit_logs"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    actor_id:Mapped[int|None]=mapped_column(ForeignKey("users.id"),nullable=True)
    action:Mapped[str]=mapped_column(String(100),nullable=False)
    target_type:Mapped[str]=mapped_column(String(60),nullable=False)
    target_id:Mapped[str]=mapped_column(String(80),default="")
    detail:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
