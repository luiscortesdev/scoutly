from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import (
    DivisionType,
    UserRoleType,
    SchoolTypeEnum,
    ClimateType,
    AcademicRigorType
)

class UserSearchPreferenceBase(BaseModel):
    title: str
    divisions: list[DivisionType]
    user_role_desire: UserRoleType
    school_type: SchoolTypeEnum
    climate: ClimateType
    program_rank: int
    academic_rigor: AcademicRigorType
    min_act: int
    min_sat: int
    user_test_score_tolerance: int
    max_distance: int
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
    divisions: list[DivisionType] | None = None
    user_role_desire: UserRoleType | None = None
    school_type: SchoolTypeEnum | None = None
    climate: ClimateType | None = None
    program_rank: int | None = None
    academic_rigor: AcademicRigorType | None = None
    min_act: int | None = None
    min_sat: int | None = None
    user_test_score_tolerance: int | None = None
    max_distance: int | None = None
    preferred_regions: list[int] | None = None
    school_size: list[int] | None = None
    school_setting: list[int] | None = None