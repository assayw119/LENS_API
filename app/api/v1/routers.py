from fastapi import APIRouter
from app.api.v1.endpoints import query, llm, order, user, table

router = APIRouter()
router.include_router(query.router, prefix="/query", tags=["Query"])
router.include_router(llm.router, prefix="/llm", tags=["LLM"])
router.include_router(order.router, prefix="/data", tags=["Data"])
router.include_router(user.router, prefix="/user", tags=["User"],)
router.include_router(table.router, prefix="/table", tags=["Table"],)
