from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    startup_name: Optional[str] = None
    startup_segment: Optional[str] = None
    startup_trl: Optional[int] = None
    startup_area: Optional[str] = None
    startup_description: Optional[str] = None
    preferred_regions: Optional[List[str]] = None
    preferred_categories: Optional[List[str]] = None
    min_amount: Optional[str] = None
    alert_frequency: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    startup_name: Optional[str] = None
    startup_segment: Optional[str] = None
    startup_trl: Optional[int] = None
    startup_area: Optional[str] = None
    startup_description: Optional[str] = None
    preferred_regions: Optional[List[str]] = None
    preferred_categories: Optional[List[str]] = None
    min_amount: Optional[str] = None
    alert_frequency: Optional[str] = None

    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Opportunity schemas
class OpportunityBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    region: Optional[str] = None
    deadline: Optional[datetime] = None
    amount: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    external_id: str
    tags: Optional[List[str]] = None

class Opportunity(OpportunityBase):
    id: int
    external_id: str
    relevance_score: float
    tags: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_favorite: Optional[bool] = False

    class Config:
        from_attributes = True

# Search schemas
class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10

class SearchResponse(BaseModel):
    query: str
    results: List[Opportunity]
    total: int
    response_text: Optional[str] = None

# Agent schemas
class AgentStatus(BaseModel):
    name: str
    status: str
    last_run: Optional[datetime] = None
    success_rate: float
    total_processed: int

class AgentLogEntry(BaseModel):
    id: int
    agent_name: str
    action: str
    status: str
    details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True