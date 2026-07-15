from datetime import datetime
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import (
    User, WeightHistory, FoodHistory, WaterHistory,
    StepHistory, SleepHistory, ExerciseHistory
)


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None) -> User:
    user = await get_user(session, telegram_id)
    if user:
        user.username = username
        user.last_active_at = datetime.utcnow()
        await session.commit()
        return user
    user = User(telegram_id=telegram_id, username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def personal_id_exists(session: AsyncSession, personal_id: str, exclude_telegram_id: int | None = None) -> bool:
    query = select(User).where(User.personal_id == personal_id)
    if exclude_telegram_id is not None:
        query = query.where(User.telegram_id != exclude_telegram_id)
    return await session.scalar(query) is not None


async def update_user(session: AsyncSession, user: User, **values) -> User:
    for key, value in values.items():
        setattr(user, key, value)
    user.last_active_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)
    return user


async def add_weight(session: AsyncSession, user: User, weight: float) -> None:
    user.current_weight_kg = weight
    session.add(WeightHistory(user_id=user.id, weight_kg=weight))
    await session.commit()


async def add_food(session: AsyncSession, user: User, data: dict) -> None:
    session.add(FoodHistory(
        user_id=user.id,
        title=str(data.get("title", "Ovqat")),
        calories=float(data.get("calories", 0)),
        protein_g=float(data.get("protein_g", 0)),
        fat_g=float(data.get("fat_g", 0)),
        carbs_g=float(data.get("carbs_g", 0)),
        details=str(data.get("note", "")),
    ))
    await session.commit()


async def add_water(session: AsyncSession, user: User, amount: int) -> None:
    session.add(WaterHistory(user_id=user.id, amount_ml=amount))
    await session.commit()


async def add_steps(session: AsyncSession, user: User, steps: int) -> None:
    session.add(StepHistory(user_id=user.id, steps=steps))
    await session.commit()


async def add_sleep(session: AsyncSession, user: User, hours: float) -> None:
    session.add(SleepHistory(user_id=user.id, hours=hours))
    await session.commit()


async def add_exercise(session: AsyncSession, user: User, title: str, minutes: int) -> None:
    session.add(ExerciseHistory(user_id=user.id, title=title, minutes=minutes))
    await session.commit()


async def get_weight_history(session: AsyncSession, user: User, limit: int = 12):
    rows = await session.scalars(
        select(WeightHistory).where(WeightHistory.user_id == user.id)
        .order_by(desc(WeightHistory.recorded_at)).limit(limit)
    )
    return list(rows)


async def today_totals(session: AsyncSession, user: User) -> dict:
    since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async def total(model, column):
        return await session.scalar(
            select(func.coalesce(func.sum(column), 0))
            .where(model.user_id == user.id, model.recorded_at >= since)
        )
    return {
        "water": int(await total(WaterHistory, WaterHistory.amount_ml) or 0),
        "steps": int(await total(StepHistory, StepHistory.steps) or 0),
        "calories": float(await total(FoodHistory, FoodHistory.calories) or 0),
        "exercise": int(await total(ExerciseHistory, ExerciseHistory.minutes) or 0),
    }


async def admin_stats(session: AsyncSession) -> dict:
    total = await session.scalar(select(func.count(User.id))) or 0
    completed = await session.scalar(
        select(func.count(User.id)).where(User.personal_id.is_not(None))
    ) or 0
    return {"total": total, "completed": completed}


async def find_by_personal_id(session: AsyncSession, personal_id: str) -> User | None:
    return await session.scalar(select(User).where(User.personal_id == personal_id))

