from fastapi import APIRouter


router = APIRouter()

@router.post("/register")
async def register(**_):
    pass

@router.post("/login")
async def login(**_):
    pass

@router.post("/refresh")
async def refresh(**_):
    pass


# TODO: Check security, make routes