from fastapi import APIRouter
from api.v1.endpoints import query, llm, order

router = APIRouter()
router.include_router(query.router, prefix="/query", tags=["Query"])
router.include_router(llm.router, prefix="/llm", tags=["LLM"])
router.include_router(order.router, prefix="/data", tags=["Data"])