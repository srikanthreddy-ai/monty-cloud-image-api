from fastapi import FastAPI
from app.api import routes_images

app = FastAPI(title="Image API")

# Include Routers
app.include_router(routes_images.router)

# Root route
@app.get("/")
def health_check():
    return {"status": "ok"}
