from fastapi import FastAPI
from app.routers import mailRouter
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware

from app.models.email import Email

app = FastAPI()
app.include_router(mailRouter.router, prefix="/mail")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def app_init():
    client = AsyncIOMotorClient(
        "mongodb+srv://boskotomicevic4_db_user:kkJAe50ZNcnzMMSS@maillist.ligclnx.mongodb.net/?retryWrites=true&w=majority"
    )
    await init_beanie(database=client["MailList"], document_models=[Email])

app.include_router(mailRouter.router)
