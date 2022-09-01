from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from database import get_session
from dependencies.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from model import User, Role, UserToRole
from schemas import Token, UserIn, UserRead

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 43200

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    user = UserRead(username=current_user.username, email=current_user.email)
    return user

@router.get("/users/me/items")
def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]

@router.post("/users", response_model=UserRead)
def sign_up(user: UserIn, session: Session = Depends(get_session)):
    hashed_password = get_password_hash(user.password)
    role = session.query(Role).filter(Role.name == "ROLE_USER").first()
    user_to_role = UserToRole()
    user_to_role.role = role
    new_user = User(email=user.email, username=user.username, password=hashed_password)
    new_user.roles.append(user_to_role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return UserRead(username=new_user.username, email=new_user.email)
