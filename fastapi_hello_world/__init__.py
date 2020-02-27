from fastapi.applications import FastAPI 
from .examples import router as examples_router

app = FastAPI()
app.include_router(examples_router)
