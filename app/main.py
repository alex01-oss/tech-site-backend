import os.path
from contextlib import asynccontextmanager
from datetime import datetime, UTC

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

from app.api.dependencies import get_db
from app.api.routes import auth, filters, users, catalog, cart, blog, media, menu, autocomplete
from app.tasks.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan_context(app_instance: FastAPI):
    app_instance.state.limiter = Limiter(key_func=get_remote_address) # type: ignore
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Search App API", lifespan=lifespan_context)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(catalog.router)
app.include_router(cart.router)
app.include_router(blog.router)
app.include_router(media.router)
app.include_router(menu.router)
app.include_router(filters.router)
app.include_router(autocomplete.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(UTC)}


@app.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unhealthy")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
