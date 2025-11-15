from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "CookMate backend is working!"}
