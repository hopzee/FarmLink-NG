import os,tempfile,pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from farmlink.database import Base
from farmlink import models
@pytest.fixture
def db():
    fd,path=tempfile.mkstemp(suffix=".db"); os.close(fd)
    engine=create_engine(f"sqlite:///{path}",connect_args={"check_same_thread":False}); Base.metadata.create_all(engine)
    Session=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
    with Session() as session: yield session
    engine.dispose(); os.unlink(path)
