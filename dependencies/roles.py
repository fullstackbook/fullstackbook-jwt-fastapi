from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from database import get_session
from model import Role, User, UserToRole
from routers.auth import get_current_active_user

def admin_role(session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    roles = session.query(Role).filter(Role.name.in_(['ROLE_ADMIN']))
    role_ids = [role.id for role in roles]
    user_to_roles = session.query(UserToRole).filter(UserToRole.user_id == current_user.id).filter(UserToRole.role_id.in_(role_ids)).all()
    if len(user_to_roles) == 0:
        raise HTTPException(403, "Unauthorized.")
    return current_user

def moderator_role(session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    roles = session.query(Role).filter(Role.name.in_(['ROLE_MODERATOR']))
    role_ids = [role.id for role in roles]
    user_to_roles = session.query(UserToRole).filter(UserToRole.user_id == current_user.id).filter(UserToRole.role_id.in_(role_ids)).all()
    if len(user_to_roles) == 0:
        raise HTTPException(403, "Unauthorized.")
    return current_user

def user_role(session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    roles = session.query(Role).filter(Role.name.in_(['ROLE_USER', 'ROLE_MODERATOR', 'ROLE_ADMIN']))
    role_ids = [role.id for role in roles]
    user_to_roles = session.query(UserToRole).filter(UserToRole.user_id == current_user.id).filter(UserToRole.role_id.in_(role_ids)).all()
    if len(user_to_roles) == 0:
        raise HTTPException(403, "Unauthorized.")
    return current_user