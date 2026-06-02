from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class ProjectCreate(BaseModel):
    name: str
    github_url: str


class BuildRequest(BaseModel):
    project_id: int

class DeployRequest(BaseModel):
    project_id: int