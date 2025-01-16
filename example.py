# Robyn身份验证和授权示例
# 为了限制对犯罪数据的访问，Batman 在应用程序中添加了身份验证和授权。他决定使用 JWT（JSON Web Token）进行身份验证。他为用户创建了一个新表，并添加了一个用于用户注册的端点。



# 用户模型
# 蝙蝠侠添加了一个新的用户模型来代表可以访问该应用程序的用户。
# 具有基本身份验证的示例请求
# models.py
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    
    def __repr__(self):
        return "<User(id={id}, username={username}, hashed_password={hashed_password})>".format(
            id=self.id,
            username=self.username,
            hashed_password=self.hashed_password,
        )

# 然后在crud.py中，他添加了一个新方法来创建用户。

# 具有基本身份验证的示例请求
# crud.py
# also need to do pip install passlib[bcrypt]

from sqlalchemy.orm import Session
from .models import User

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: User):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 身份验证实用程序
# 蝙蝠侠创建了实用函数来处理身份验证，包括散列密码和验证密码。

# 带有持有者令牌的示例请求
# crud.py
# also need to do pip install passlib[bcrypt]
# pip install "python-jose[cryptography]"
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

ALGORITHM = "HS256"
SECRET_KEY = "your_secret_key"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    created_token = create_access_token(data={"sub": .username})
    return created_token


# 用户注册端点
# 蝙蝠侠添加了一个新的端点以允许用户注册。

# 设置路线
from . import crud

@app.post("/users/register")
async def register_user(request):
    user = request.json()
    with SessionLocal() as db:
        created_user = crud.create_user(db, user)
    return created_user

@app.post("/users/login")
async def login_user(request):
    user = request.json()
    with SessionLocal() as db:
        token = crud.authenticate_user(db, **user)

    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")


    return {"access_token": token}
