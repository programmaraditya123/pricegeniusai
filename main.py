from fastapi import FastAPI
from app.llms.GoogleChatModel import googleModelInvoke

app = FastAPI()

@app.get("/")
def home():
    return {"backend " : "is runing"}


@app.get("/getllmresponse")
def llm():
    return googleModelInvoke("hello")


