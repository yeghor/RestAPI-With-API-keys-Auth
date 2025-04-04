from fastapi import FastAPI
from typing import List, Dict, Any, Optional, Annotated
from schemas import Stats

app = FastAPI()

@app.get("/")
def test() -> Dict:
    return {"detail": "Hello World"}