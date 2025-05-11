from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(prefix="/users", tags=["users"])