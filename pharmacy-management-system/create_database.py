from database.session import engine, Base

# مهم جداً
from models.all_models import * # noqa

print("Creating database...")

Base.metadata.create_all(bind=engine)

print("Database created successfully!")