import os.path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.routes.auth.get_user import get_user_router
from app.api.routes.auth.login import login_router
from app.api.routes.auth.logout import logout_router
from app.api.routes.auth.refresh_token import refresh_token_router
from app.api.routes.auth.register import register_router
from app.api.routes.cart.add_to_cart import add_router
from app.api.routes.cart.get_cart import get_cart_router
from app.api.routes.cart.remove_from_cart import remove_router
from app.api.routes.catalog.catalog import catalog_router
from app.api.routes.catalog.catalog_item import get_catalog_item_router
from app.api.routes.other.menu import menu_router
from app.api.routes.other.static import static_router
from app.api.routes.posts.create_post import create_post_router
from app.api.routes.posts.delete_post import delete_post_router
from app.api.routes.posts.edit_post import edit_post_router
from app.api.routes.posts.get_all_posts import get_all_posts_router
from app.api.routes.posts.get_post import get_post_router
from app.api.routes.posts.upload_image import upload_image_router

app = FastAPI(title="Search App API")
#
# redis_client = redis.Redis(
#     host=settings.CACHE_REDIS_HOST,
#     port=settings.CACHE_REDIS_PORT,
#     db=settings.CACHE_REDIS_DB,
#     decode_responses=settings.CACHE_REDIS_DECODE_RESPONSES
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
app.include_router(static_router)

app.include_router(login_router)
app.include_router(register_router)
app.include_router(refresh_token_router)
app.include_router(logout_router)
app.include_router(get_user_router)

app.include_router(get_cart_router)
app.include_router(add_router)
app.include_router(remove_router)

app.include_router(catalog_router)

app.include_router(create_post_router)
app.include_router(edit_post_router)
app.include_router(delete_post_router)
app.include_router(get_post_router)
app.include_router(get_all_posts_router)
app.include_router(upload_image_router)
app.include_router(get_catalog_item_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)