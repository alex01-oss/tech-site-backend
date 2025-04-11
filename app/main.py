import os.path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.routes.add_to_cart import add_router
from app.api.routes.catalog import catalog_router
from app.api.routes.get_cart import get_cart_router
from app.api.routes.login import login_router
from app.api.routes.menu import menu_router
from app.api.routes.refresh_token import refresh_token_router
from app.api.routes.register import register_router
from app.api.routes.remove_from_cart import remove_router
from app.api.routes.static import static_router

app = FastAPI(title="Search App API")
#
# redis_client = redis.Redis(
#     host=settings.CACHE_REDIS_HOST,
#     port=settings.CACHE_REDIS_PORT,
#     db=settings.CACHE_REDIS_DB,
#     decode_responses=settings.CACHE_REDIS_DECODE_RESPONSES,
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(menu_router)
app.include_router(login_router)
app.include_router(register_router)
app.include_router(get_cart_router)
app.include_router(add_router)
app.include_router(catalog_router)
app.include_router(remove_router)
app.include_router(refresh_token_router)
app.include_router(static_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)