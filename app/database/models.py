from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )

    personal_id: Mapped[str | None] = mapped_column(
        String(7),
        unique=True,
        index=True,
        nullable=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        String(2),
        default="uz",
    )

    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    height_cm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    current_weight_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    goal: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    activity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    accepted_terms: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    last_active_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    weights: Mapped[list["WeightHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    foods: Mapped[list["FoodHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class WeightHistory(Base):
    __tablename__ = "weight_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    weight_kg: Mapped[float] = mapped_column(
        Float,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user: Mapped[User] = relationship(
        back_populates="weights",
    )


class FoodHistory(Base):
    __tablename__ = "food_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
    )

    calories: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    protein_g: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    fat_g: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    carbs_g: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user: Mapped[User] = relationship(
        back_populates="foods",
    )


class WaterHistory(Base):
    __tablename__ = "water_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    amount_ml: Mapped[int] = mapped_column(
        Integer,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class StepHistory(Base):
    __tablename__ = "step_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    steps: Mapped[int] = mapped_column(
        Integer,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class SleepHistory(Base):
    __tablename__ = "sleep_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    hours: Mapped[float] = mapped_column(
        Float,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class ExerciseHistory(Base):
    __tablename__ = "exercise_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
    )

    minutes: Mapped[int] = mapped_column(
        Integer,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
