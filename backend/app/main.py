from fastapi import FastAPI

app = FastAPI(
    title="egeapi",
    description="Platform for EGE preparation",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the hell"}