from fastapi import FastAPI

from database import create_db_and_tables
from routes import auth_router, health_check, category,user, item, tenant, log
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import close_mongo, connect_mongo, log_requests

app = FastAPI(title="Template INFO8B API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# salva no Mongo todas as chamadas feitas em qualquer endpoint
app.middleware("http")(log_requests)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    connect_mongo()


@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo()


app.include_router(auth_router)
app.include_router(health_check)
app.include_router(category)
app.include_router(user)
app.include_router(item)
app.include_router(tenant)
app.include_router(log)