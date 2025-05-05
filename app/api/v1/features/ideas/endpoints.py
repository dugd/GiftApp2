from uuid import UUID

from fastapi import APIRouter


router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("/")
def create(data: dict):
    pass


@router.get("/my")
def index_my(archived: bool = False):
    pass


@router.get("/global")
def index_global(archived: bool = False):
    pass


@router.get("/{idea_id}")
def get(idea_id: UUID):
    pass


@router.patch("/{idea_id}")
def update_info(
        idea_id: UUID,
        data: dict,
):
    pass


@router.delete("/{idea_id}")
def delete(idea_id: UUID):
    pass


router.post("/{idea_id}/archive")
def archive(idea_id: UUID):
    pass