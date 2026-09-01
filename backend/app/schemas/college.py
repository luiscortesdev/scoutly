from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CollegeRead(BaseModel):
    unit_id: int
    opeid: str | None = None
    opeid6: str | None = None
    name: str
    city: str
    state: str
    zip: str
    accreditation_agency: str | None = None
    institution_url: str | None = None
    net_price_calculator_url: str | None = None
    is_main_campus: bool | None = None
    region: int | None = None
    locale: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    admissions_rate: float | None = None
    
    sat_reading_25th: int | None = None
    sat_reading_75th: int | None = None
    sat_reading_50th: int | None = None
    sat_math_25th: int | None = None
    sat_math_75th: int | None = None
    sat_math_50th: int | None = None
    sat_total_25th: int | None = None
    sat_total_75th: int | None = None
    sat_total_50th: int | None = None
    sat_avg: int | None = None
    
    act_25th: int | None = None
    act_75th: int | None = None
    act_50th: int | None = None
    
    undergrad_size: int | None = None
    graduate_size: int | None = None
    in_state_tuition: int | None = None
    out_of_state_tuition: int | None = None
    school_type: str | None = None
    address: str | None = None
    median_earnings_9yrs: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class CollegeReadWithPrograms(CollegeRead):
    pass