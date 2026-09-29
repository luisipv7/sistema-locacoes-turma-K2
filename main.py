from fastapi import FastAPI

from database import create_db_and_tables
from routes import auth_router
from fastapi.middleware.cors import CORSMiddleware

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


app.include_router(auth_router)
