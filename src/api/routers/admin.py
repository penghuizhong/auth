# src/api/routers/admin.py
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from core.config import settings
from core.database import get_engine
from models.chat_session import ChatSession
from models.user import User

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")
        
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD.get_secret_value():
            request.session.update({"token": "admin_token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True

class UserAdmin(ModelView, model=User):
    # 此处为您保留了上一回合建议的汉化配置位置，您可以随时开启
    # name = "用户"
    # name_plural = "用户管理"
    column_list = ["id", "email", "nickname", "is_active", "created_at"]
    column_searchable_list = ["email", "nickname"]
    column_sortable_list = ["created_at"]

class ChatSessionAdmin(ModelView, model=ChatSession):
    # name = "会话"
    # name_plural = "会话管理"
    column_list = [ "title", "is_deleted", "created_at"]
    column_searchable_list = ["title"]
    column_sortable_list = ["created_at"]
    


# 👇 核心黑魔法：接收主 app 实例，在此处完成挂载
def setup_admin(app: FastAPI):
    admin = Admin(
        app=app,
        engine=get_engine(),
        authentication_backend=AdminAuth(secret_key=settings.AUTH_SECRET.get_secret_value()),
        title="方圆智版 Admin",
        base_url="/admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(ChatSessionAdmin)