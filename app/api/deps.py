from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.users import User

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
                     db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Invalid authentication credentials")
    
    try:
        payload = jwt.decode(credentials.credentials,
                             settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise credentials_exception
        
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user