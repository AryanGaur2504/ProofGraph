import os, hashlib, hmac, secrets
from datetime import datetime, timedelta, timezone
import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .db import get_db
from .models import User

SECRET = os.environ.get('PROOFGRAPH_JWT_SECRET', 'DEMO-ONLY-CHANGE-BEFORE-DEPLOYMENT')
AUTH = HTTPBearer(auto_error=False)
ROLES = {'Institution', 'Scrutiny Officer', 'Senior Officer', 'Admin', 'Auditor'}
WRITE_ROLES = {'Scrutiny Officer', 'Senior Officer', 'Admin'}

def hash_password(password: str):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 260_000)
    return 'pbkdf2_sha256$260000$' + salt.hex() + '$' + dk.hex()

def check_password(password: str, encoded: str):
    try:
        algo, count, salt, digest = encoded.split('$')
        if algo != 'pbkdf2_sha256': return False
        candidate = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(count))
        return hmac.compare_digest(candidate, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False

def make_token(user: User):
    return jwt.encode({'sub': str(user.id), 'role': user.role, 'exp': datetime.now(timezone.utc) + timedelta(hours=8)}, SECRET, algorithm='HS256')

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(AUTH), db: Session = Depends(get_db)):
    if not credentials: raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Sign in to continue')
    try:
        claims = jwt.decode(credentials.credentials, SECRET, algorithms=['HS256'])
        user = db.get(User, int(claims['sub']))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(401, 'Token invalid or expired')
    if not user or not user.active: raise HTTPException(401, 'Account unavailable')
    return user

def require_roles(*roles):
    def validator(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(403, 'Insufficient role permissions')
        return user
    return validator

def check_case_access(db, user, app):
    if not app: raise HTTPException(404, 'Case not found')
    if user.role == 'Institution' and user.institution_id != app.institution_id:
        raise HTTPException(403, 'This case is not owned by your institution')
    return app

_fernet = None
def encrypt_sensitive(value):
    global _fernet
    key = os.environ.get('PROOFGRAPH_ENCRYPTION_KEY')
    if not key: return 'DEMO-UNENCRYPTED:' + value  # test data ONLY; production must set key
    if _fernet is None: _fernet = Fernet(key.encode())
    return _fernet.encrypt(value.encode()).decode()

def mask_sensitive(value, role):
    return value if role in {'Admin','Senior Officer'} else '•••••• (restricted)'
