from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime

# ==================== USER SCHEMAS ====================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 UTF-8 bytes")
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 UTF-8 bytes")
        return value

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ==================== PROFILE SCHEMAS ====================

class ProfileCreate(BaseModel):
    college: str
    branch: str
    gpa: float = Field(ge=0, le=10)
    college_tier: int = Field(default=2, ge=1, le=3)
    current_location: Optional[str] = None
    home_location: Optional[str] = None
    distance_from_home: float = Field(default=0.0, ge=0)
    career_goal: Optional[str] = None
    preferred_domains: Optional[List[str]] = []
    preferred_roles: Optional[List[str]] = []
    internships_count: int = 0
    projects_count: int = 0
    current_skills: Optional[List[str]] = []
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    wants_to_switch_after: Optional[int] = Field(default=None, ge=0)
    study_time_available: float = Field(default=0.0, ge=0, le=24)

class ProfileResponse(ProfileCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== OFFER SCHEMAS ====================

class OfferCreate(BaseModel):
    company_name: str
    company_type: str
    role: str
    job_description: Optional[str] = None
    ctc: float = Field(gt=0)
    base_salary: Optional[float] = None
    location: str
    is_mass_recruiter: bool = False
    bond_period: int = Field(default=0, ge=0)
    skill_requirements: Optional[List[str]] = []
    work_mode: str = "Office"
    deadline: Optional[datetime] = None

class OfferResponse(OfferCreate):
    id: int
    user_id: int
    received_date: datetime
    is_accepted: bool
    predicted_2yr_salary: Optional[float] = None
    skill_match_score: Optional[float] = None
    switch_probability: Optional[float] = None
    workload_score: Optional[float] = None
    recommendation_score: Optional[float] = None
    
    class Config:
        from_attributes = True

# ==================== PREDICTION INPUT SCHEMAS ====================

class SalaryPredictionInput(BaseModel):
    company_type: str
    role: str
    location: str
    current_ctc: float
    college_tier: int
    gpa: float

class SwitchPredictionInput(BaseModel):
    current_role: str
    skill_gap: float
    study_time_available: float
    wants_to_switch_after: int

class WorkloadPredictionInput(BaseModel):
    company_name: str
    company_type: str
    role: str
    work_mode: str

class JobDescription(BaseModel):
    description: str

class CompareOffersInput(BaseModel):
    offer_ids: List[int]

# ==================== FEEDBACK SCHEMAS ====================

class FeedbackCreate(BaseModel):
    offer_id: int
    actual_experience: str
    actual_salary_after_1yr: Optional[float] = None
    actual_salary_after_2yr: Optional[float] = None
    did_switch: bool = False
    switched_after_months: Optional[int] = None
    workload_rating: int
    growth_rating: int
    satisfaction_rating: int
