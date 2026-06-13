from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import engine, Base
from src.api.routes import auth, admin_music, admin_users, owner_controls, entity_builder, workflow_full, crm, rules, plugins, admin_tickets, owner_reports
from strawberry.fastapi import GraphQLRouter
from src.api.graphql import schema

app = FastAPI(title="TEOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(admin_music.router)
app.include_router(admin_users.router)
app.include_router(owner_controls.router)
app.include_router(entity_builder.router)
app.include_router(workflow_full.router)
app.include_router(crm.router)
app.include_router(rules.router)
app.include_router(plugins.router)
app.include_router(admin_tickets.router)
app.include_router(owner_reports.router)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
