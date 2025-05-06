from app.models import User, AdminUser
from app.ideas.idea_schemas import IdeaModel


class IdeaPolicy:
    def __init__(self, user: User, idea: IdeaModel):
        self.user = user
        self.idea = idea

    def can_create(self):
        return isinstance(self.user, AdminUser) or not self.idea.is_global

    def can_view(self):
        return isinstance(self.user, AdminUser) or self.idea.is_global or self.idea.user_id == self.user.id

    def can_edit(self):
        return isinstance(self.user, AdminUser) or self.idea.user_id == self.user.id

    def can_delete(self):
        return isinstance(self.user, AdminUser) or self.idea.user_id == self.user.id
