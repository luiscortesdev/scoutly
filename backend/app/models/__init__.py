# import all models at runtime
from app.models.base import Base

from app.models.college import College
from app.models.program import Program
from app.models.player import Player
from app.models.program_event import ProgramEvent
from app.models.user import User
from app.models.user_preference import UserSearchPreference
from app.models.user_event import UserEvent
from app.models.saved_match import SavedMatch