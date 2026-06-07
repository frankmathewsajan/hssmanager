from ninja import Router
from ninja_jwt.authentication import JWTAuth

from .roster import router as roster_router
from .admissions import router as admissions_router
from .scanner import router as scanner_router

# The Master Student Router
router = Router(tags=["Students"], auth=JWTAuth())

router.add_router("/roster", roster_router)       # -> /api/students/roster/
router.add_router("/onboard", admissions_router)  # -> /api/students/onboard/
router.add_router("/scanner", scanner_router)     # -> /api/students/scanner/