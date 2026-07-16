from aiogram import Router

from app.handlers.start import router as start_router
from app.handlers.profile import router as profile_router
from app.handlers.body import router as body_router
from app.handlers.slimwell import router as slimwell_router
from app.handlers.exercises import router as exercises_router
from app.handlers.results import router as results_router
from app.handlers.habits import router as habits_router


router = Router()

router.include_router(start_router)
router.include_router(profile_router)
router.include_router(body_router)
router.include_router(slimwell_router)
router.include_router(exercises_router)
router.include_router(results_router)
router.include_router(habits_router)
