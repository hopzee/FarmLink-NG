from io import BytesIO
from uuid import uuid4
from PIL import Image,UnidentifiedImageError
from farmlink.config import settings
FORMATS={"JPEG":".jpg","PNG":".png","WEBP":".webp"}
def save_product_image(uploaded):
    if uploaded is None: return ""
    raw=uploaded.getvalue()
    if len(raw)>settings.MAX_UPLOAD_MB*1024*1024: raise ValueError(f"Image must be at most {settings.MAX_UPLOAD_MB} MB.")
    try:
        image=Image.open(BytesIO(raw)); image.verify(); image=Image.open(BytesIO(raw))
    except (UnidentifiedImageError,OSError): raise ValueError("Upload a valid JPEG, PNG, or WebP image.")
    if image.format not in FORMATS: raise ValueError("Upload a JPEG, PNG, or WebP image.")
    image.thumbnail((1600,1600)); settings.UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
    path=settings.UPLOAD_DIR/f"{uuid4().hex}{FORMATS[image.format]}"
    image.convert("RGB").save(path,quality=88,optimize=True)
    return str(path)
