import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BASE_DIR=Path(__file__).resolve().parent.parent
class Settings:
    APP_ENV=os.getenv("APP_ENV","development").lower()
    DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./data/farmlink.db")
    UPLOAD_DIR=Path(os.getenv("UPLOAD_DIR",str(BASE_DIR/"uploads")))
    MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB","5"))
settings=Settings()
