import os
import jwt

secret = os.environ['SECRET']

def readToken(token: str):
  return jwt.decode(token, secret, algorithm="HS256")