from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    ExerciseHistory,
    FoodHistory,
    SleepHistory,
    StepHistory,
    User,
    WaterHistory,
    WeightHistory,
)


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_personal_id(session: AsyncSession, personal_id: str) -> User | None:
    result = await session.execute(select(User).where(User.personal_id == personal_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, **kwargs) -> User:
    user = User(**kwargs)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, telegram_id: int, **kwargs) -> None:
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(**kwargs, last_active_at=datetime.utcnow())
    )
    await session.commit()


async def update_last_active(session: AsyncSession, telegram_id: int) -> None:
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(last_active_at=datetime.utcnow())
    )
    await session.commit()


async def get_users_count(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count(User.id)))
    return int(result or 0)


async def get_completed_users_count(session: AsyncSession) -> int:
    result = await session.scalar(
        select(func.count(User.id)).where(
            User.personal_id.is_not(None),
            User.name.is_not(None),
        )
    )
    return int(result or 0)


async def add_weight(session: AsyncSession, user_id: int, weight: float) -> WeightHistory:
    row = WeightHistory(user_id=user_id, weight_kg=weight)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def get_weight_history(
    session: AsyncSession,
    user_id: int,
    limit: int | None = None,
) -> list[WeightHistory]:
    query = (
        select(WeightHistory)
        .where(WeightHistory.user_id == user_id)
        .order_by(WeightHistory.recorded_at.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def add_water(session: AsyncSession, user_id: int, amount: int) -> WaterHistory:
    row = WaterHistory(user_id=user_id, amount_ml=amount)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def add_steps(session: AsyncSession, user_id: int, steps: int) -> StepHistory:
    row = StepHistory(user_id=user_id, steps=steps)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def add_sleep(session: AsyncSession, user_id: int, hours: float) -> SleepHistory:
    row = SleepHistory(user_id=user_id, hours=hours)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def add_food(
    session: AsyncSession,
    user_id: int,
    title: str,
    calories: float,
    protein: float,
    fat: float,
    carbs: float,
    details: str = "",
) -> FoodHistory:
    row = FoodHistory(
        user_id=user_id,
        title=title,
        calories=calories,
        protein_g=protein,
        fat_g=fat,
        carbs_g=carbs,
        details=details,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def add_exercise(
    session: AsyncSession,
    user_id: int,
    title: str,
    minutes: int,
) -> ExerciseHistory:
    row = ExerciseHistory(user_id=user_id, title=title, minutes=minutes)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


def today_start() -> datetime:
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


async def get_today_water(session: AsyncSession, user_id: int) -> int:
    result = await session.scalar(
        select(func.coalesce(func.sum(WaterHistory.amount_ml), 0)).where(
            WaterHistory.user_id == user_id,
            WaterHistory.recorded_at >= today_start(),
        )
    )
    return int(result or 0)


async def get_today_steps(session: AsyncSession, user_id: int) -> int:
    result = await session.scalar(
        select(func.coalesce(func.sum(StepHistory.steps), 0)).where(
            StepHistory.user_id == user_id,
            StepHistory.recorded_at >= today_start(),
        )
    )
    return int(result or 0)


async def get_today_sleep(session: AsyncSession, user_id: int) -> float:
    result = await session.scalar(
        select(SleepHistory.hours)
        .where(
            SleepHistory.user_id == user_id,
            SleepHistory.recorded_at >= today_start(),
        )
        .order_by(SleepHistory.recorded_at.desc())
        .limit(1)
    )
    return float(result or 0)


async def get_today_exercise_minutes(session: AsyncSession, user_id: int) -> int:
    result = await session.scalar(
        select(func.coalesce(func.sum(ExerciseHistory.minutes), 0)).where(
            ExerciseHistory.user_id == user_id,
            ExerciseHistory.recorded_at >= today_start(),
        )
    )
    return int(result or 0)


async def get_today_food_calories(session: AsyncSession, user_id: int) -> float:
    result = await session.scalar(
        select(func.coalesce(func.sum(FoodHistory.calories), 0)).where(
            FoodHistory.user_id == user_id,
            FoodHistory.recorded_at >= today_start(),
        )
    )
    return float(result or 0)


async def get_today_summary(
    session: AsyncSession,
    user_id: int,
) -> dict[str, int | float]:
    return {
        "water_ml": await get_today_water(session, user_id),
        "steps": await get_today_steps(session, user_id),
        "sleep_hours": await get_today_sleep(session, user_id),
        "exercise_minutes": await get_today_exercise_minutes(session, user_id),
        "food_calories": await get_today_food_calories(session, user_id),
    }
