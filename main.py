from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes.admin import router as admin_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.nodes import router as nodes_router
from app.api.routes.supervisor import router as supervisor_router
from app.db.database import Base, engine
from app.db.seed import seed_database

app = FastAPI(
    title="MineMesh API",
    version="1.0.0",
    description="MineMesh backend API with Swagger documentation for frontend integration.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(nodes_router)
app.include_router(alerts_router)
app.include_router(supervisor_router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    seed_database()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://example.com/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def read_root():
    return {"message": "MineMesh API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
