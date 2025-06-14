from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.utils.function_calling import convert_to_openai_tool
from dotenv import load_dotenv
from schema import Greet_Intro_Response, CheckBudgetInterest, Deal
from datetime import datetime

load_dotenv()

# MOCK Campaign and Brand Data
brand = "Meta"
brand_description = "Social Media tech giant"
campaign = "Meta Developer Conference"
campaign_description = "Post 3 to 4 thumbnails for the tech event"
influencer_name = "Ankesh Kumar"

converted_greet_tool = convert_to_openai_tool(Greet_Intro_Response)
converted_budgetInterest_tool = convert_to_openai_tool(CheckBudgetInterest)
converted_deal_tool = convert_to_openai_tool(Deal)

# Fixed: Get current time for proper greeting
def get_greeting_time():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

greet_prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """You are a brand owner working for the brand: {brand}, brand_description: {brand_description}
     and looking for influencers for your campaign: {campaign}.
     Here is the campaign description: {campaign_description} 
     
     Here are your tasks:
        1. Greet the user/influencer: {influencer_name} with "{greeting_time}" and give a small intro of your brand
        2. Explain the campaign details to the influencer
        
     Keep your response professional, friendly, and engaging. Make sure to use the greet_intro tool to provide your response.
     """),
    MessagesPlaceholder(variable_name="messages"),
]).partial(
    greeting_time=get_greeting_time(),
    brand=brand,
    brand_description=brand_description,
    campaign=campaign,
    campaign_description=campaign_description,
    influencer_name=influencer_name
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.3
)

greet_responder_chain = (
    greet_prompt_template 
    | llm.bind_tools(
        tools=[converted_greet_tool],
        tool_choice="Greet_Intro_Response"
    )
)


campaign_query_prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """You are an enthusiastic brand outreach assistant.

Context:
- Brand Name: {brand}
- Brand Description: {brand_description}
- Campaign Name: {campaign}
- Campaign Description: {campaign_description}

Your goal is to respond to the user's questions about the campaign with a rich, complete, and engaging overview of the event.

**Instructions:**
- Begin with a friendly greeting and introduction of the brand.
- Give a **thorough and detailed** explanation of the campaign purpose, theme, goals, and deliverables.
- Mention the **target audience**, platform(s) to be used, and expectations from the creator.
- End with an **inviting and positive** tone to encourage participation.

Make sure your response is:
- Professional and enthusiastic
- Easy to understand
- Well-structured and complete
- MAXIMUM 4-5 lines long

DO NOT skip details or respond briefly.

Now, respond based on the following message history:
"""),
    MessagesPlaceholder(variable_name="messages")
]).partial(
    brand=brand,
    brand_description=brand_description,
    campaign=campaign,
    campaign_description=campaign_description,
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.3
)

campaign_responder_chain = (
    campaign_query_prompt_template 
    | llm
)

budget_interest_chain = llm.bind_tools(
    tools=[converted_budgetInterest_tool],
    tool_choice="CheckBudgetInterest"
)

# Prompt Template for the Deal Chain
deal_prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     f"""You are a negotiation assistant working on behalf of the brand "{brand}".

Your job is to analyze the user's response and extract the following:

1. Set `isDeal = True` if the user **agrees** to the offered price or accepts the deal.
2. Set `isDeal = False` if the user **declines** or suggests a different price.
3. In all cases, extract the **final price** the user is referring to and set it as `user_price` (integer only).
   - If the user accepts, use the agreed price.
   - If the user counter-offers, use their suggested price.
   - If unclear or they reject, return the originally offered price or use `-1` if completely uninterested.

Also, return a respectful, clear `message` summarizing the result, written from the assistant's perspective.

Example Responses:

User: "Sounds good, let's proceed with ₹300."
→ `isDeal = true`, `user_price = 300`

User: "Can you do ₹310?"
→ `isDeal = false`, `user_price = 310`

User: "No thanks."
→ `isDeal = false`, `user_price = -1`

If the input is weird then don't accept the deal and Tell user that they can restart the conversation from the mailbox if they think its a technical issue also when the user rejects the offer if they change their mind

Use the `Deal` tool to return the output.
"""),
    MessagesPlaceholder(variable_name="messages"),
])

deal_chain = (
    deal_prompt_template
    | llm.bind_tools(
        tools=[converted_deal_tool],
        tool_choice="Deal"
    )
)

# Test the chains individually (uncomment to test)
if __name__ == "__main__":
    response = campaign_responder_chain.invoke()
#     from langchain_core.messages import HumanMessage
#     
#     # Test greet chain
#     test_messages = [HumanMessage(content="Hello, I'm interested in your campaign")]
#     response = greet_responder_chain.invoke({"messages": test_messages})
#     print("Greet response:", response.tool_calls[0]["args"]["greet_intro"])
#     
#     # Test budget interest chain
#     response2 = budget_interest_chain.invoke("sure!")
#     print("Budget interest response:", response2.tool_calls[0]["args"]["interest_response"])
