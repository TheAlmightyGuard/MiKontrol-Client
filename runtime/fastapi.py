from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth, guilds
import uvicorn

# FastAPI setup
app = FastAPI(
    title="MiKontrol API",
    description="API for MiKontrol Discord Bot",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(guilds.router)


# GET Endpoints
@app.get("/")
async def check_status():
    return {"status": "API is running"}



# Start Service
async def startService():
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        loop="asyncio",
        log_config=None
    )
    server = uvicorn.Server(config)
    await server.serve()
