from fastapi import APIRouter
from api.v1.endpoints import query, llm, order, user, table, history

router = APIRouter()
router.include_router(query.router, prefix="/query", tags=["Query"])
router.include_router(llm.router, prefix="/llm", tags=["LLM"])
router.include_router(order.router, prefix="/data", tags=["Data"])
router.include_router(user.router, prefix="/user", tags=["User"],)
router.include_router(table.router, prefix="/table", tags=["Table"],)
router.include_router(history.router, prefix="/history", tags=["History"],)
