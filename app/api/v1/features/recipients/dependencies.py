from app.service.recipient import RecipientService, RecipientPolicy
from app.repositories.orm.recipient import RecipientRepository
from app.api.v1.dependencies import DBSessionDepends


async def get_recipient_service(db: DBSessionDepends) -> RecipientService:
    return RecipientService(RecipientRepository(db), RecipientPolicy)