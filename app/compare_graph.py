from typing import TypedDict
from langgraph.graph import StateGraph,END
from app.agentNodes.queryUnderstanding.product_understanding import understand_product
from app.agentNodes.searchtool.search_tool_functions import search_all_platforms
from app.services.scrapservice import scrape_products

class ProductState(TypedDict):
    product_name: str
    product_link: str
    understanding: dict

    search_results : dict

    scraped_products : dict

def understanding_node(state: ProductState):

    result = understand_product(
        state["product_name"],
        state["product_link"]
    )
    state["understanding"] = result.model_dump()

    return state

async def search_node(state : ProductState):
    understanding = state["understanding"]
    query = f"""
    {understanding.get("brand", "")}
    {understanding.get("model", "")}
    {understanding.get("storage", "")}
    """
    result = await search_all_platforms(query)
    state["search_results"] = result

    return state

async def scrap_node(state):
    scraped_products = await scrape_products(state["search_results"])


    state["scraped_products"] = scraped_products

    return state


graph = StateGraph(ProductState)

graph.add_node("understanding",understanding_node)

graph.add_node("search_products",search_node)

graph.add_node("scrap_products",scrap_node)

graph.set_entry_point("understanding")

graph.add_edge("understanding","search_products")

graph.add_edge("search_products","scrap_products")

graph.add_edge("scrap_products",END)

compare_graph = graph.compile()