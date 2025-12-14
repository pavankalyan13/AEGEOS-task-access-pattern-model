from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from enum import Enum

class PersonaType(str, Enum):
    ENGINEERING = "engineering"
    IT = "it"
    SALES = "sales"

class TaskType(str, Enum):
    FEATURE_DEVELOPMENT = "feature_development"
    PRODUCTION_SUPPORT = "production_support"
    INCIDENT_RESOLUTION = "incident_resolution"
    INFRASTRUCTURE_MAINTENANCE = "infrastructure_maintenance"
    LEAD_GENERATION = "lead_generation"
    PROPOSAL_DEVELOPMENT = "proposal_development"

class AccessLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    NONE = "none"

class User(BaseModel):
    user_id: str
    name: str
    team: str
    persona: PersonaType
    location: str

class Permission(BaseModel):
    resource_type: str  # "github" or "filesystem"
    resource_path: str
    access_level: AccessLevel

class Task(BaseModel):
    task_id: str
    task_type: TaskType
    description: str
    required_permissions: List[Permission]
    persona: PersonaType

class Prompt(BaseModel):
    prompt_id: str
    text: str
    user_id: str
    mapped_tasks: List[str] = []
    confidence_score: float = 0.0

class ToolCall(BaseModel):
    tool_name: str
    resource_type: str
    resource_path: str
    action: str
    parameters: Dict = {}

class AccessRequest(BaseModel):
    user_id: str
    prompt: str
    requested_tool_calls: List[ToolCall]

class AccessResponse(BaseModel):
    allowed: bool
    mapped_tasks: List[str]
    denied_calls: List[ToolCall] = []
    reason: str = ""
