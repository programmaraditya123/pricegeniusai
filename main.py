from fastapi import FastAPI
from app.routes.llm_routes import router as llm_router
from app.expense_tracker.router import router as expense_tracker_router
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
app.include_router(expense_tracker_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"backend " : "is runing"}


 


