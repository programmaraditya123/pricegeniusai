from fastapi import FastAPI
from app.routes.llm_routes import router as llm_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PriceGeniusAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

app.include_router(llm_router,prefix="/api/v1",tags=["compare products"])

@app.get("/")
def home():
    return {"backend " : "is runing"}


 


