from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from routes import (
    auth_router,
    booking_router,
    category_router,
    health_router,
    item_router,
    tenant_router,
    user_router,
)

app = FastAPI(title="Template INFO8B API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


    


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(user_router)
app.include_router(category_router)   
app.include_router(item_router)
app.include_router(booking_router)