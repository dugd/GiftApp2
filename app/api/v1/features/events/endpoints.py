from datetime import date

from fastapi import APIRouter


router = APIRouter(prefix="/events", tags=["events"])


@router.get("/")
async def index():
    """Get all (global and user`s) next planned events"""
    pass


@router.get("/occurrences")
async def index_occurrences(from_date: date, to_date: date):
    """Get all event occurrences in date interval"""
    pass


@router.post("/")
async def create():
    """Create new event"""
    pass


@router.get("/{event_id}")
async def get():
    """Create next planned event"""
    pass


@router.patch("/{event_id}")
async def update_info():
    """update title, type fields"""
    pass


@router.delete("/{event_id}")
async def delete():
    """delete event (set to inactive)"""
    pass


@router.get("/{event_id}/occurrences")
async def get_occurrences(from_date: date, to_date: date):
    """Get event occurrences in date interval"""
    pass
