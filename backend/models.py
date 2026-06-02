from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True)

    email = Column(String(255), unique=True)

    password_hash = Column(String(255))
class Project(Base):

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255))

    github_url = Column(String(500))

    user_email = Column(String(255))

class Deployment(Base):

    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer)

    image_name = Column(String(255))

    status = Column(String(50))

    port = Column(Integer)

    container_id = Column(String(255))

    build_logs = Column(String(5000))