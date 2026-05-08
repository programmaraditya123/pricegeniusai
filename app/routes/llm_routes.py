from fastapi import APIRouter
from app.llms.GoogleChatModel import googleModelInvoke
from app.compare_graph import compare_graph
from app.agentNodes.queryUnderstanding.schemas import ProductRequest

router = APIRouter()

@router.post("/compare")
async def compare_product(data : ProductRequest):
    result = await compare_graph.ainvoke({
        "product_name" : data.product_name,
        "product_link" : data.product_link
    })
    return result
     