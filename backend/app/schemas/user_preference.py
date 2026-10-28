from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import (
    DivisionType,
    UserRoleType,
    SchoolTypeEnum,
    ClimateType,
    AcademicRigorType
)

class UserSearchPreferenceBase(BaseModel):
    title: str
    divisions: list[DivisionType] = Field(min_length=1)
    user_role_desire: UserRoleType
    school_type: SchoolTypeEnum
    climate: ClimateType
    program_rank: int = Field(ge=1, le=500) # This is the highest program rank the user wants to see (highest as in greater ranking/lower in the standings)
    academic_rigor: AcademicRigorType
    min_act: int = Field(ge=1, le=36)
    min_sat: int = Field(ge=400, le=1600)
    user_test_score_tolerance: int = Field(ge=0, le=3) # This will likely be moved into an enum
    max_distance: int = Field(ge=0) # 0 means no maximum distance. The user will be presented with different max choices not an integer input
    preferred_regions: list[int]
    school_size: list[int]
    school_setting: list[int]
    
class UserSearchPreferenceCreate(UserSearchPreferenceBase):
    pass

class UserSearchPreferenceRead(UserSearchPreferenceBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# validate incoming patch requests. fields can be None
class UserSearchPreferenceUpdate(BaseModel):
    title: str | None = None
    divisions: list[DivisionType] | None = Field(default=None, min_length=1)
    user_role_desire: UserRoleType | None = None
    school_type: SchoolTypeEnum | None = None
    climate: ClimateType | None = None
    program_rank: int | None = Field(default=None, ge=1, le=500)
    academic_rigor: AcademicRigorType | None = None
    min_act: int | None = Field(default=None, ge=1, le=36)
    min_sat: int | None = Field(default=None, ge=400, le=1600)
    user_test_score_tolerance: int | None = Field(default=None, ge=0, le=3)
    max_distance: int | None = Field(default=None, ge=0)
    preferred_regions: list[int] | None = None
    school_size: list[int] | None = None
    school_setting: list[int] | None = None