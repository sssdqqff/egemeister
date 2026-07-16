from fastapi import FastAPI

app = FastAPI(
    title="egeapi",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the hell"}