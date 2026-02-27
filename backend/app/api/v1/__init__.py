from fastapi import APIRouter

from app.api.v1 import admin, ai_signal, auth, nifty, options, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(nifty.router)
api_router.include_router(options.router)
api_router.include_router(ai_signal.router)
api_router.include_router(admin.router)
