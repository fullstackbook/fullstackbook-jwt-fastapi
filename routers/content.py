from fastapi import APIRouter, Depends

from dependencies.roles import admin_role, moderator_role, user_role

router = APIRouter()

@router.get("/admin")
def admin(current_user = Depends(admin_role)):
    return "admin content"

@router.get("/user")
def user(current_user = Depends(user_role)):
    return "user content"

@router.get("/moderator")
def moderator(current_user = Depends(moderator_role)):
    return "moderator content"

@router.get("/all")
def all():
    return "public content"
