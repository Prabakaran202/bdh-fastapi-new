import os
import sys
import argparse
import urllib.request
import urllib.error
import json


# ... (Previous Boilerplate Content remains the same) ...

# ── New Frontend (TK) Boilerplate ──────────────────────────────────

INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Frontend</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        <h1>Welcome to {project_name}</h1>
        <p>Status: <span id="status">Connecting...</span></p>
        <div id="user-list"></div>
    </div>
    <script src="script.js"></script>
</body>
</html>
'''

STYLE_CSS = '''body {
    font-family: sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f4f4f9;
}
#app {
    text-align: center;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
'''

SCRIPT_JS = '''async function fetchData() {
    try {
        const response = await fetch('http://localhost:8000/');
        const data = await response.json();
        document.getElementById('status').innerText = data.message;
    } catch (err) {
        document.getElementById('status').innerText = 'Backend Offline';
    }
}
fetchData();
'''

# ── Colors ─────────────────────────────────────────────────────────
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

# ── Updated Functions ──────────────────────────────────────────────

def print_tree(project_name, admin_mode=False, fd_mode=False):
    print(f"\n{CYAN}  {project_name}/{RESET}")
    print(f"  {CYAN}  app/{RESET}")
    print(f"  {GREEN}    main.py{RESET}")
    if fd_mode:
        print(f"  {CYAN}  frontend/{RESET}")
        print(f"  {GREEN}    index.html{RESET}")
        print(f"  {GREEN}    style.css{RESET}")
        print(f"  {GREEN}    script.js{RESET}")
    # ... rest of tree ...

def create_project(project_name: str, ai_mode: bool = False, admin_mode: bool = False, fd_mode: bool = False):
    # (Banner and AI logic stays the same)
    
    if os.path.exists(project_name):
        print(f"{RED}'{project_name}' already exists!{RESET}")
        sys.exit(1)

    folders = [
        f"{project_name}/app/routers",
        f"{project_name}/app/models",
        f"{project_name}/app/schemas",
        f"{project_name}/app/crud",
    ]

    if fd_mode:
        folders.append(f"{project_name}/frontend")

    # Define standard files
    router_name = "users"
    files = {
        f"{project_name}/app/__init__.py": "",
        f"{project_name}/app/main.py": MAIN_PY_ADMIN if admin_mode else MAIN_PY,
        f"{project_name}/app/database.py": DATABASE_PY,
        f"{project_name}/app/routers/{router_name}.py": USERS_ROUTER,
        f"{project_name}/.env": ENV_FILE,
        f"{project_name}/requirements.txt": REQUIREMENTS_ADMIN if admin_mode else REQUIREMENTS,
    }

    # Add Frontend files if -fd is used
    if fd_mode:
        files[f"{project_name}/frontend/index.html"] = INDEX_HTML.format(project_name=project_name)
        files[f"{project_name}/frontend/style.css"] = STYLE_CSS
        files[f"{project_name}/frontend/script.js"] = SCRIPT_JS

    if admin_mode:
        files[f"{project_name}/app/admin.py"] = ADMIN_PY

    # Create directories and write files
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)

    print(f"{GREEN}{BOLD}Project '{project_name}' created successfully with --fd frontend!{RESET}")


   

# ── Boilerplate Content ─────────────────────────────────────────────

MAIN_PY = '''from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="My FastAPI App",
    description="Built with bdh-fastapi-new CLI",
    version="1.0.0"
)

app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
'''

MAIN_PY_ADMIN = '''from fastapi import FastAPI
from app.routers import users
from app.database import engine
from app.admin import UserAdmin
from sqladmin import Admin

app = FastAPI(
    title="My FastAPI App",
    description="Built with bdh-fastapi-new CLI",
    version="1.0.0"
)

# Admin Panel → /admin
admin = Admin(app, engine)
admin.add_view(UserAdmin)

# Routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
'''

ADMIN_PY = '''from sqladmin import ModelView
from app.models.user import User

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
'''

DATABASE_PY = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

USERS_ROUTER = '''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users(db: Session = Depends(get_db)):
    """Get all users."""
    return {"users": []}

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    return {"user_id": user_id}
'''

USER_MODEL = '''from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
'''

USER_SCHEMA = '''from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
'''

USER_CRUD = '''from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
'''

REQUIREMENTS = '''fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic[email]
'''

REQUIREMENTS_ADMIN = '''fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic[email]
sqladmin
'''

GITIGNORE = '''venv/
__pycache__/
*.pyc
.env
*.db
.DS_Store
'''

ENV_FILE = '''DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
'''

README_TEMPLATE = '''# {project_name}

> Built with [bdh-fastapi-new](https://pypi.org/project/bdh-fastapi-new/) CLI

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

- GET / -> Health check
- GET /docs -> Swagger UI
{admin_line}
'''

# ── Colors ─────────────────────────────────────────────────────────

CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

def banner():
    print(f"""
{CYAN}{BOLD}
  ███████╗ █████╗ ███████╗████████╗ █████╗ ██████╗ ██╗    ███╗   ██╗███████╗██╗    ██╗
  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║    ████╗  ██║██╔════╝██║    ██║
  █████╗  ███████║███████╗   ██║   ███████║██████╔╝██║    ██╔██╗ ██║█████╗  ██║ █╗ ██║
  ██╔══╝  ██╔══██║╚════██║   ██║   ██╔══██║██╔═══╝ ██║    ██║╚██╗██║██╔══╝  ██║███╗██║
  ██║     ██║  ██║███████║   ██║   ██║  ██║██║     ██║    ██║ ╚████║███████╗╚███╔███╔╝
  ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝
{RESET}{DIM}  ⚡ bdh-fastapi-new — FastAPI Project Generator by BackendDeveloperHub{RESET}
""")

# ── BDH AI Generator ───────────────────────────────────────────────

def generate_from_bdh(description: str):
    print(f"\n{CYAN}AI generating your FastAPI backend...{RESET}\n")

    payload = json.dumps({
        "prompt": f"Create a {description}"
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://ai-api-builder.onrender.com/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=100) as response:
            result = json.loads(response.read().decode("utf-8"))
            api_code = result.get("api_code", "")
            if api_code:
                print(f"{GREEN}AI generation successful!{RESET}")
                return {"generated_main": api_code}
            return None
    except Exception as e:
        print(f"{RED}AI Error: {e} - using default template{RESET}")
        return None

# ── Banner ─────────────────────────────────────────────────────────

def banner():
    print(f"""
{CYAN}{BOLD}  bdh-fastapi-new v2.1{RESET}
{DIM}  AI-Powered FastAPI Generator by BackendDeveloperHub{RESET}
""")

def print_tree(project_name, admin_mode=False):
    print(f"\n{CYAN}  {project_name}/{RESET}")
    print(f"  {CYAN}app/{RESET}")
    print(f"  {GREEN}  main.py{RESET}")
    print(f"  {GREEN}  database.py{RESET}")
    if admin_mode:
        print(f"  {YELLOW}  admin.py{RESET}")
    print(f"  {CYAN}  routers/{RESET}")
    print(f"  {CYAN}  models/{RESET}")
    print(f"  {CYAN}  schemas/{RESET}")
    print(f"  {CYAN}  crud/{RESET}")
    print(f"  {YELLOW}  .env{RESET}")
    print(f"  {YELLOW}  requirements.txt{RESET}")

# ── Core Generator ─────────────────────────────────────────────────

def create_project(project_name: str, ai_mode: bool = False, admin_mode: bool = False):
    banner()

    if os.path.exists(project_name):
        print(f"{RED}'{project_name}' already exists!{RESET}")
        sys.exit(1)

    # ── AI Mode ──
    ai_data = None
    if ai_mode:
        print(f"\n{CYAN}Describe your API:{RESET} ", end="")
        description = input().strip()

        if description:
            ai_data = generate_from_bdh(description)

    print(f"{BOLD}Creating: {CYAN}{project_name}{RESET}\n")

    folders = [
        f"{project_name}/app/routers",
        f"{project_name}/app/models",
        f"{project_name}/app/schemas",
        f"{project_name}/app/crud",
    ]

    # ── File Contents ──
    router_name    = "users"
    router_content = USERS_ROUTER
    model_content  = USER_MODEL
    schema_content = USER_SCHEMA
    crud_content   = USER_CRUD

    # AI generated main.py use பண்ணு
    if ai_data and ai_data.get("generated_main"):
        main_content = ai_data["generated_main"]
    elif admin_mode:
        main_content = MAIN_PY_ADMIN
    else:
        main_content = MAIN_PY

    req_content = REQUIREMENTS_ADMIN if admin_mode else REQUIREMENTS
    admin_line  = "- GET /admin -> Admin Panel" if admin_mode else ""

    files = {
        f"{project_name}/app/__init__.py": "",
        f"{project_name}/app/main.py": main_content,
        f"{project_name}/app/database.py": DATABASE_PY,
        f"{project_name}/app/routers/__init__.py": "",
        f"{project_name}/app/routers/{router_name}.py": router_content,
        f"{project_name}/app/models/__init__.py": "",
        f"{project_name}/app/models/{router_name}.py": model_content,
        f"{project_name}/app/schemas/__init__.py": "",
        f"{project_name}/app/schemas/{router_name}.py": schema_content,
        f"{project_name}/app/crud/__init__.py": "",
        f"{project_name}/app/crud/{router_name}.py": crud_content,
        f"{project_name}/.env": ENV_FILE,
        f"{project_name}/.gitignore": GITIGNORE,
        f"{project_name}/requirements.txt": req_content,
        f"{project_name}/README.md": README_TEMPLATE.format(
            project_name=project_name,
            admin_line=admin_line
        ),
    }

    if admin_mode:
        files[f"{project_name}/app/admin.py"] = ADMIN_PY

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)

    print_tree(project_name, admin_mode)

    flags = []
    if ai_data:
        flags.append(f"{GREEN}AI Generated{RESET}")
    if admin_mode:
        flags.append(f"{YELLOW}Admin Panel{RESET}")
    if not flags:
        flags.append(f"{CYAN}Default Template{RESET}")

    print(f"\n{GREEN}{BOLD}'{project_name}' ready! {' + '.join(flags)}{RESET}")

    admin_note = f"\n  {YELLOW}Admin -> http://localhost:8000/admin{RESET}" if admin_mode else ""
    print(f"""
  cd {project_name}
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload
{admin_note}
  {DIM}Swagger -> http://localhost:8000/docs{RESET}
""")

def main():
    parser = argparse.ArgumentParser(
        prog="bdh-fastapi-new",
        description="AI-Powered FastAPI Generator by BackendDeveloperHub"
    )
    parser.add_argument("project_name", help="Project name")
    parser.add_argument("--ai", action="store_true", help="AI-powered code generation")
    parser.add_argument("--admin", action="store_true", help="Include SQLAdmin panel")
    parser.add_argument("--fd", action="store_true", help="Include Frontend toolkit structure")

    args = parser.parse_args()
    create_project(args.project_name, ai_mode=args.ai, admin_mode=args.admin,fd_mode=args.fd)

if __name__ == "__main__":
    main()
