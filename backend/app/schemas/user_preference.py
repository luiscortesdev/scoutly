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