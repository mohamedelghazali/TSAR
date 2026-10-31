"""TSAR reference: secure REST handler with FastAPI."""
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
from jose import jwt, JWTError

app = FastAPI()

JWT_SECRET = "read-from-env"  # replaced at runtime with env var reference
JWT_ALG = "HS256"
JWT_AUDIENCE = "tsar-api"

class TokenPayload(BaseModel):
    sub: str
    aud: str
    exp: int
    jti: str

def verify_token(authorization: Annotated[str | None, Header()] = None) -> TokenPayload:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="missing token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG],
                            audience=JWT_AUDIENCE,
                            options={"require": ["exp", "sub", "aud", "jti"]})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="invalid token")
    return TokenPayload(**claims)

class Resource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    owner_id: str
    name: str = Field(min_length=1, max_length=200)

class ResourceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)

@app.get("/v1/resources/{resource_id}", response_model=Resource)
async def get_resource(resource_id: UUID,
                       user: Annotated[TokenPayload, Depends(verify_token)]):
    resource = load_resource(resource_id)  # parameterized DB call
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if resource.owner_id != user.sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return resource

@app.post("/v1/resources", response_model=Resource, status_code=201)
async def create_resource(body: ResourceInput,
                          user: Annotated[TokenPayload, Depends(verify_token)]):
    return create_in_db(body, user.sub)

@app.exception_handler(Exception)
async def handle_any(request, exc):
    return JSONResponse(status_code=500, content={"error": "internal_error"})

def load_resource(resource_id: UUID): ...
def create_in_db(body: ResourceInput, owner_id: str): ...
