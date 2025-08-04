from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot_agent import get_chain
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
qa_chain = get_chain()

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat(request: ChatRequest):
    response = qa_chain.run(request.question)
    return {"response": response}
