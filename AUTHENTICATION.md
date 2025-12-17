# User Authentication & Authorization

This guide covers adding user authentication and multi-user support to the application.

## Implementation Plan

### 1. Add User Model

Update `backend/src/database/models.py`:

```python
class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user")
    training_modules = relationship("TrainingModule", back_populates="user")
```

### 2. Update Existing Models

Add user_id foreign keys:

```python
# In Resume model
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
user = relationship("User", back_populates="resumes")

# In TrainingModule model
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
user = relationship("User", back_populates="training_modules")
```

### 3. Authentication Service

Create `backend/src/services/auth.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database.database import SessionLocal
from src.database.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

### 4. Add Auth Routes

Create `backend/src/api/auth_routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from src.database.database import SessionLocal
from src.database.models import User
from src.services.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(SessionLocal)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### 5. Update Existing Routes

Add authentication to routes in `backend/src/api/routes.py`:

```python
from src.services.auth import get_current_user
from src.database.models import User

@router.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ... existing code ...
    resume = Resume(
        user_id=current_user.id,  # Add this
        filename=parsed_data["filename"],
        # ... rest of fields
    )
```

### 6. Frontend Authentication

Create `frontend/src/lib/auth.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function login(email: string, password: string) {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) throw new Error('Login failed');
  return response.json();
}

export async function register(email: string, password: string, fullName?: string) {
  const response = await fetch(`${API_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  
  if (!response.ok) throw new Error('Registration failed');
  return response.json();
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function setToken(token: string) {
  localStorage.setItem('access_token', token);
}

export function removeToken() {
  localStorage.removeItem('access_token');
}
```

### 7. Add Login/Register Pages

Create `frontend/src/app/login/page.tsx` and `frontend/src/app/register/page.tsx`.

### 8. Protect Routes

Create `frontend/src/components/ProtectedRoute.tsx`:

```typescript
'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getToken } from '@/lib/auth'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      router.push('/login')
    } else {
      setLoading(false)
    }
  }, [router])

  if (loading) return <div>Loading...</div>
  return <>{children}</>
}
```

## Quick Implementation

Run these commands to add auth:

```bash
# Backend
cd backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# Update main.py to include auth router
# Update routes to require authentication
# Run migrations to add User table
```

## Next Steps

1. Add password reset functionality
2. Add email verification
3. Add role-based access control (admin/user)
4. Add user profile management
5. Add session management



