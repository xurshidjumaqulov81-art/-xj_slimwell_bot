from datetime import datetime, timedelta
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.base import (
    ExerciseHistory, FoodHistory, SleepHistory, StepHistory,
    User, WaterHistory, WeightHistory
)

settings = get_settings()


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None
) -> User:
    user = await get_user(session, telegram_id)
    if user:
        user.username = username
        user.last_active_at = datetime.utcnow()
        await session.commit()
        return user

    last_id = await session.scalar(select(func.max(User.id))) or 0
    number = settings.start_id + last_id
    slimwell_id = f"{number:07d}"[-7:]
    user = User(
        telegram_id=telegram_id,
        username=username,
        slimwell_id=slimwell_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


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


async def add_food(
    session: AsyncSession, user: User, title: str, calories: float,
    protein: float, fat: float, carbs: float, details: str
) -> None:
    session.add(FoodHistory(
        user_id=user.id, title=title, calories=calories,
        protein_g=protein, fat_g=fat, carbs_g=carbs, details=details
    ))
    await session.commit()


async def weight_history(session: AsyncSession, user: User, limit: int = 10):
    result = await session.scalars(
        select(WeightHistory).where(WeightHistory.user_id == user.id)
        .order_by(desc(WeightHistory.recorded_at)).limit(limit)
    )
    return list(result)


async def today_totals(session: AsyncSession, user: User) -> dict:
    since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    water = await session.scalar(
        select(func.coalesce(func.sum(WaterHistory.amount_ml), 0))
        .where(WaterHistory.user_id == user.id, WaterHistory.recorded_at >= since)
    )
    calories = await session.scalar(
        select(func.coalesce(func.sum(FoodHistory.calories), 0))
        .where(FoodHistory.user_id == user.id, FoodHistory.recorded_at >= since)
    )
    steps = await session.scalar(
        select(func.coalesce(func.sum(StepHistory.steps), 0))
        .where(StepHistory.user_id == user.id, StepHistory.recorded_at >= since)
    )
    exercise = await session.scalar(
        select(func.coalesce(func.sum(ExerciseHistory.minutes), 0))
        .where(ExerciseHistory.user_id == user.id, ExerciseHistory.recorded_at >= since)
    )
    return {"water": int(water or 0), "calories": float(calories or 0),
            "steps": int(steps or 0), "exercise": int(exercise or 0)}


async def admin_stats(session: AsyncSession) -> dict:
    total = await session.scalar(select(func.count(User.id))) or 0
    since = datetime.utcnow() - timedelta(days=7)
    active = await session.scalar(
        select(func.count(User.id)).where(User.last_active_at >= since)
    ) or 0
    return {"total": total, "active": active}


async def search_user_by_slimwell_id(session: AsyncSession, slimwell_id: str) -> User | None:
    return await session.scalar(select(User).where(User.slimwell_id == slimwell_id))
