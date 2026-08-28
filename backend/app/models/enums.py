from enum import StrEnum

class GenderType(StrEnum):
    men = "men"
    women = "women"

class DivisionType(StrEnum):
    ncaa_d1 = "ncaa_d1"
    ncaa_d2 = "ncaa_d2"
    ncaa_d3 = "ncaa_d3"
    naia = "naia"
    njcaa_i = "njcaa_i"
    njcaa_ii = "njcaa_ii"
    njcaa_iii = "njcaa_iii"

class UserRoleType(StrEnum):
    best_player = "best_player"
    travel_squad = "travel_squad"
    redshirt_freshman = "redshirt_freshman"
    walk_on = "walk_on"

class SchoolTypeEnum(StrEnum):
    public = "public"
    private_nonprofit = "private_nonprofit"
    private_forprofit = "private_forprofit"

class ClimateType(StrEnum):
    warm = "warm"
    moderate = "moderate"
    cold = "cold"

class EventLevelType(StrEnum):
    local = "local"
    state = "state"
    regional = "regional"
    national = "national"

class RecruitingTierType(StrEnum):
    reach = "reach"
    target = "target"
    safety = "safety"
    undecided = "undecided"
    
class AcademicRigorType(StrEnum):
    low_rigor = "low_rigor"
    medium_rigor = "medium_rigor"
    high_rigor = "high_rigor"