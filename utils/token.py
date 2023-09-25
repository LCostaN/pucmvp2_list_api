import os
import jwt

secret = os.environ.get('SECRET') or "PUCMVP22023"

def readToken(token: str):
  return jwt.decode(token, secret, algorithms=["HS256"])