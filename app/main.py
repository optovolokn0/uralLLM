from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(title="VK Post Generator")

app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")