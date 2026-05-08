#here we build a node to understand the query of the product

from langchain_core.prompts import ChatPromptTemplate
from app.agentNodes.queryUnderstanding.schemas import ProductUnderstanding
from app.llms.GoogleChatModel import llm

structured_llm = llm.with_structured_output(ProductUnderstanding)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an advanced ecommerce product understanding AI.

        Your job is to analyze any type of product from any ecommerce platform.

        Extract and normalize product information into structured data.

        Rules:
        - Identify the actual product category correctly.
        - Extract only clearly available information.
        - If information is missing, return null.
        - Generate useful search keywords.
        - Do not hallucinate specifications.
        - Return structured output only.

        Extract:
        - brand
        - product_name
        - model
        - category
        - subcategory
        - color
        - size
        - material
        - storage
        - weight
        - gender
        - specifications
        - keywords

        specifications should contain important attributes relevant to the product category.

        Example Smartphone:

        {{
          "ram": "8GB",
          "storage": "256GB"
        }}

        Example Watch:

        {{
          "strap_material": "Leather",
          "dial_size": "44mm"
        }}

        Example Toy:

        {{
          "age_group": "3+",
          "material": "Plastic"
        }}
        """
    ),
    (
        "human",
        """
        Product Name: {product_name}

        Product Link: {product_link}
        """
    )
])

chain = prompt | structured_llm

def understand_product(product_name, product_link):
    return chain.invoke({
        "product_name": product_name,
        "product_link": product_link
    })