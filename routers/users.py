from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from database import get_session, engine
from model import User, Role, UserToRole

router = APIRouter()


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserIn(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    username: str
    email: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    with Session(engine) as session:
        results = session.query(User).filter(User.username == username)
        user = results.first()

        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    with Session(engine) as session:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        results = session.query(User).filter(User.username == token_data.username)
        user = results.first()
        if user is None:
            raise credentials_exception
        return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


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
