from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from calculator import add, sub, mul, div

app = FastAPI(title="Calculator API", version="1.0.0")

class CalcRequest(BaseModel):
    a: float
    b: float

class CalcResponse(BaseModel):
    result: float

@app.post("/api/v1/add", response_model=CalcResponse)
def add_view(payload: CalcRequest):
    return CalcResponse(result=add(payload.a, payload.b))

@app.post("/api/v1/sub", response_model=CalcResponse)
def sub_view(payload: CalcRequest):
    return CalcResponse(result=sub(payload.a, payload.b))

@app.post("/api/v1/mul", response_model=CalcResponse)
def mul_view(payload: CalcRequest):
    return CalcResponse(result=mul(payload.a, payload.b))

@app.post("/api/v1/div", response_model=CalcResponse)
def div_view(payload: CalcRequest):
    try:
        result = div(payload.a, payload.b)
    except ZeroDivisionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CalcResponse(result=result)
