from schemas import UserLogin
from fastapi import FastAPI
from sqlalchemy.orm import Session

from database import SessionLocal
from database import engine

from models import Base
from models import User
from models import Project
from models import Deployment

from schemas import UserCreate
from schemas import ProjectCreate

from auth import hash_password
from auth import verify_password
from auth import create_access_token

from github_service import clone_repo

from docker_service import build_image

from deploy_service import run_container

from container_service import list_containers
from container_service import stop_container
from container_service import restart_container

from auth import verify_token

from schemas import BuildRequest

from schemas import BuildRequest

from schemas import DeployRequest

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "CloudForge Running"
    }


@app.post("/register")
def register(user: UserCreate):

    db: Session = SessionLocal()

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User Registered",
        "user_id": new_user.id
    }


@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        return {
            "message": "User not found"
        }

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        return {
            "message": "Wrong password"
        }

    token = create_access_token(
        {
            "sub": existing_user.email
        }
    )

    return {
        "message": "Login Successful",
        "access_token": token
    }


@app.post("/project")
def create_project(
    project: ProjectCreate,
    token: str
):

    payload = verify_token(token)

    if not payload:

        return {
            "message": "Invalid Token"
        }

    db = SessionLocal()

    new_project = Project(
        name=project.name,
        github_url=project.github_url,
        user_email=payload["sub"]
    )

    db.add(new_project)

    db.commit()

    db.refresh(new_project)

    return {
        "message": "Project Created",
        "project_id": new_project.id,
        "owner": payload["sub"]
    }

@app.post("/clone")
def clone_github_repo(project: ProjectCreate):

    path = clone_repo(
        project.github_url
    )

    return {
        "message": "Repository Cloned",
        "path": path
    }


@app.post("/build")
def build_project(
    request: BuildRequest,
    token: str
):

    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid Token"
        }

    db = SessionLocal()

    project = db.query(Project).filter(
        Project.id == request.project_id
    ).first()

    if not project:
        return {
            "message": "Project Not Found"
        }

    if project.user_email != payload["sub"]:
        return {
            "message": "Unauthorized"
        }

    repo_name = project.github_url.split("/")[-1]

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    repo_path = clone_repo(
        project.github_url
    )

    result = build_image(
        repo_path,
        repo_name.lower()
    )

    status = "SUCCESS"

    if result.get("returncode") != 0:
        status = "FAILED"

    deployment = Deployment(
        project_id=project.id,
        image_name=repo_name.lower(),
        status=status,
        build_logs=result.get("stderr", "")[:4000]
    )

    db.add(deployment)
    db.commit()

    return {
    "status": status,
    "project_id": project.id,
    "stdout": result.get("stdout", ""),
    "stderr": result.get("stderr", "")
}

@app.get("/deployments")
def get_deployments():

    db = SessionLocal()

    deployments = db.query(
        Deployment
    ).all()

    result = []

    for deployment in deployments:

        result.append({
            "id": deployment.id,
            "project_id": deployment.project_id,
            "image_name": deployment.image_name,
            "status": deployment.status
        })

    return result

@app.post("/deploy")
def deploy_project(
    request: DeployRequest,
    token: str
):

    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid Token"
        }

    db = SessionLocal()

    project = db.query(Project).filter(
        Project.id == request.project_id
    ).first()

    if not project:
        return {
            "message": "Project Not Found"
        }

    if project.user_email != payload["sub"]:
        return {
            "message": "Unauthorized"
        }

    latest = db.query(Deployment).order_by(
        Deployment.id.desc()
    ).first()

    port = 8081

    if latest and latest.port:
        port = latest.port + 1

    image_name = project.github_url.split("/")[-1]

    if image_name.endswith(".git"):
        image_name = image_name[:-4]

    result = run_container(
        image_name.lower(),
        port
    )

    container_id = result.get(
        "stdout",
        ""
    ).strip()

    deployment = Deployment(
        project_id=project.id,
        image_name=image_name.lower(),
        status="RUNNING",
        port=port,
        container_id=container_id,
        build_logs=""
    )

    db.add(deployment)

    db.commit()

    return {
        "message": "Deployment Successful",
        "port": port,
        "url": f"http://localhost:{port}",
        "container_id": container_id
    }

@app.get("/containers")
def get_containers():

    return list_containers()

@app.get("/build-logs")
def get_build_logs():

    db = SessionLocal()

    deployments = db.query(
        Deployment
    ).all()

    result = []

    for deployment in deployments:

        result.append({
            "id": deployment.id,
            "status": deployment.status,
            "logs": deployment.build_logs
        })

    return result

@app.get("/users")
def get_users():

    db = SessionLocal()

    users = db.query(User).all()

    result = []

    for user in users:

        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    return result

from fastapi import Header

from fastapi import Header

@app.get("/profile")
def profile(token: str):

    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid Token"
        }

    return {
        "message": "Authorized",
        "user": payload
    }

@app.get("/my-projects")
def my_projects(token: str):

    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid Token"
        }

    db = SessionLocal()

    projects = db.query(Project).filter(
        Project.user_email == payload["sub"]
    ).all()

    result = []

    for project in projects:

        result.append({
            "id": project.id,
            "name": project.name,
            "github_url": project.github_url,
            "owner": project.user_email
        })

    return result

@app.delete("/project/{project_id}")
def delete_project(
    project_id: int,
    token: str
):

    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid Token"
        }

    db = SessionLocal()

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        return {
            "message": "Project Not Found"
        }

    if project.user_email != payload["sub"]:
        return {
            "message": "Unauthorized"
        }

    db.delete(project)

    db.commit()

    return {
        "message": "Project Deleted"
    }

@app.post("/stop-container")
def stop_running_container(
    container_id: str
):

    result = stop_container(
        container_id
    )

    return result

@app.post("/restart-container")
def restart_running_container(
    container_id: str
):

    result = restart_container(
        container_id
    )

    return result