from fastapi import FastAPI

app = FastAPI(
    title="LATAM User Management API",
    description="RESTful API for user management built with FastAPI.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}