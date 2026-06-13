import strawberry
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.music.models import Track
from src.modules.service_vpn.models import ServicePlan

@strawberry.type
class TrackType:
    id: int
    title: str
    artist: str
    plays: int

@strawberry.type
class PlanType:
    id: int
    name: str
    price: float

@strawberry.type
class Query:
    @strawberry.field
    async def tracks(self, search: Optional[str] = None) -> List[TrackType]:
        async with async_session() as db:
            stmt = select(Track)
            if search:
                stmt = stmt.where(Track.title.ilike(f"%{search}%"))
            result = await db.execute(stmt.limit(20))
            tracks = result.scalars().all()
            return [TrackType(id=t.id, title=t.title, artist=t.artist, plays=t.plays) for t in tracks]

    @strawberry.field
    async def service_plans(self) -> List[PlanType]:
        async with async_session() as db:
            result = await db.execute(select(ServicePlan).where(ServicePlan.is_active == True))
            plans = result.scalars().all()
            return [PlanType(id=p.id, name=p.name, price=p.price) for p in plans]

schema = strawberry.Schema(query=Query)
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_track(self, title: str, artist: str, genre: str = "") -> TrackType:
        async with async_session() as db:
            track = Track(title=title, artist=artist, genre=genre)
            db.add(track)
            await db.commit()
            return TrackType(id=track.id, title=track.title, artist=track.artist, plays=0)

    @strawberry.mutation
    async def submit_deposit(self, user_id: int, amount: float, description: str) -> str:
        async with async_session() as db:
            from src.modules.wallet_payment.service import wallet_service
            tx = await wallet_service.deposit_request(db, user_id, amount, description)
            return f"Transaction {tx.id} created, pending approval."

schema = strawberry.Schema(query=Query, mutation=Mutation)
