from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    User,
    WeightHistory,
    WaterHistory,
    StepHistory,
    SleepHistory,
    FoodHistory,
    ExerciseHistory,
)


# ==========================
# USER
# ==========================

async def get_user(
    session: AsyncSession,
    telegram_id: int,
):
    result = await session.execute(
        select(User).where(
            User.telegram_id == telegram_id
        )
    )

    return result.scalar_one_or_none()


async def get_user_by_personal_id(
    session: AsyncSession,
    personal_id: str,
):
    result = await session.execute(
        select(User).where(
            User.personal_id == personal_id
        )
    )

    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    **kwargs,
):
    user = User(**kwargs)

    session.add(user)

    await session.commit()

    await session.refresh(user)

    return user


async def update_user(
    session: AsyncSession,
    telegram_id: int,
    **kwargs,
):
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(**kwargs)
    )

    await session.commit()


async def get_users_count(
    session: AsyncSession,
):
    result = await session.execute(
        select(User)
    )

    return len(result.scalars().all())


# ==========================
# WEIGHT
# ==========================

async def add_weight(
    session: AsyncSession,
    user_id: int,
    weight: float,
):
    row = WeightHistory(
        user_id=user_id,
        weight_kg=weight,
    )

    session.add(row)

    await session.commit()


async def get_weight_history(
    session: AsyncSession,
    user_id: int,
):
    result = await session.execute(
        select(WeightHistory)
        .where(
            WeightHistory.user_id == user_id
        )
        .order_by(
            WeightHistory.recorded_at.desc()
        )
    )

    return result.scalars().all()


# ==========================
# WATER
# ==========================

async def add_water(
    session: AsyncSession,
    user_id: int,
    amount: int,
):
    row = WaterHistory(
        user_id=user_id,
        amount_ml=amount,
    )

    session.add(row)

    await session.commit()


# ==========================
# STEPS
# ==========================

async def add_steps(
    session: AsyncSession,
    user_id: int,
    steps: int,
):
    row = StepHistory(
        user_id=user_id,
        steps=steps,
    )

    session.add(row)

    await session.commit()


# ==========================
# SLEEP
# ==========================

async def add_sleep(
    session: AsyncSession,
    user_id: int,
    hours: float,
):
    row = SleepHistory(
        user_id=user_id,
        hours=hours,
    )

    session.add(row)

    await session.commit()


# ==========================
# FOOD
# ==========================

async def add_food(
    session: AsyncSession,
    user_id: int,
    title: str,
    calories: float,
    protein: float,
    fat: float,
    carbs: float,
    details: str,
):
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


# ==========================
# EXERCISE
# ==========================

async def add_exercise(
    session: AsyncSession,
    user_id: int,
    title: str,
    minutes: int,
):
    row = ExerciseHistory(
        user_id=user_id,
        title=title,
        minutes=minutes,
    )

    session.add(row)

    await session.commit()


# ==========================
# LAST ACTIVE
# ==========================

async def update_last_active(
    session: AsyncSession,
    telegram_id: int,
):
    await session.execute(
        update(User)
        .where(
            User.telegram_id == telegram_id
        )
        .values(
            last_active_at=datetime.utcnow()
        )
    )

    await session.commit()
