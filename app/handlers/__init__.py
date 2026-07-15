from aiogram import Router

from app.handlers.profile import (
    router as profile_router,
)
from app.handlers.start import (
    router as start_router,
)


router = Router()

router.include_router(start_router)
router.include_router(profile_router)
