from typing import TypedDict, List
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage
from langgraph.graph import END, StateGraph
from chains import greet_responder_chain, budget_interest_chain, campaign_responder_chain, deal_chain
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(verbose=True)

class NegotiationState(TypedDict):
    final_response: str
    agreed_price: int
    isDeal: bool
    init_budget: int  # Initial Budget
    messages: List[BaseMessage]  # Required for MessageGraph compatibility

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.3
)

# Use StateGraph for better state management
graph = StateGraph(NegotiationState)

GREET_INTRO = "greet_intro"
INTERRUPT = "interrupt"
CAMPAIGN_QUERY = "campaign_query"
BUDGET_NEGOTIATOR = "budget_negotiator"

def greet_node(state: NegotiationState) -> dict:
    """
    Wrapper for greet_responder_chain to ensure proper return format
    """
    # Get current messages or create initial message if empty
    current_messages = state.get("messages", [])
    
    # If no messages exist, create an initial human message to trigger the greeting
    if not current_messages:
        current_messages = [HumanMessage(content="Hello, I'm interested in your campaign")]
    
    try:
        # Invoke your chain with the messages
        response = greet_responder_chain.invoke({"messages": current_messages})
        
        # Extract the greeting from tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            greeting_text = response.tool_calls[0]["args"]["greet_intro"]
            
            # Create an AI message with the greeting
            ai_message = AIMessage(content=greeting_text)
            
            print(greeting_text)

            # Return state updates as dictionary
            return {
                "final_response": greeting_text,
                "messages": current_messages + [ai_message]
            }
        else:
            # Fallback if no tool calls
            return {
                "final_response": str(response.content) if hasattr(response, 'content') else str(response),
                "messages": current_messages + [response] if hasattr(response, 'content') else current_messages
            }
            
    except Exception as e:
        print(f"Error in greet_node: {e}")
        return {
            "final_response": "Hello! I'm excited to discuss our campaign opportunity with you.",
            "messages": current_messages + [AIMessage(content="Hello! I'm excited to discuss our campaign opportunity with you.")]
        }


def checkBudgetInterest(state: NegotiationState) -> str: 
    try:
        # Asking if User/Influencer is interested in knowing the budget
        get_interest = input("Would you like to know the Budget? (yes/no): ")
        isInterested_response = budget_interest_chain.invoke(get_interest)

        isInterested = isInterested_response.tool_calls[0]["args"]["interest_response"]
        other_query = isInterested_response.tool_calls[0]["args"]["other_query"]
        state["messages"] += [HumanMessage(get_interest)]
        print(f"isInterested: {isInterested}, other_query: {other_query}")

        if other_query:
            print("Other query: ", other_query)
            classification = llm.invoke(f"What is the user's intent? Message: '{get_interest}'. Reply with one word: campaign_query/exit")
            intent = classification.content.strip().lower()
            print("Intent: ",intent)
            if intent == "campaign_query":
                return CAMPAIGN_QUERY
            else:
                state["messages"] += AIMessage(content="Looks like some error occured")
                return END
            
        elif isInterested:
            print("We liked your interest!")
            return BUDGET_NEGOTIATOR

        Exit_Msg = "Sad to see you go but hope to have a deal in future!"
        state["messages"] += [AIMessage(content=Exit_Msg)]
        state["final_response"] = Exit_Msg
        print(state["final_response"])
        return END
        
    except Exception as e:
        print(f"Error in checkBudgetInterest: {e}")
        return END

def campaign_query(state: NegotiationState) -> str:
    current_msg = state["messages"]

    response = campaign_responder_chain.invoke({"messages": current_msg})

    state["messages"] += [AIMessage(content=response.content)]
    state["final_response"] = response.content

    print("QUERY: ",response.content)
    return state

def budget_negotiator(state) -> dict:
    print("Reached budget negotiation node.")

    init_budget = state["init_budget"]
    acceptable_limit = init_budget * 1.10  # 10% more than initial budget

    # Present the initial offer
    agreement_ques = (
        f"\nWe’re offering a budget of ₹{init_budget}, which we believe reflects the value of this collaboration. "
        "Would you be comfortable proceeding with this offer?"
    )
    state["messages"] += [AIMessage(content=agreement_ques)]

    # Get user input
    ask_user = input(agreement_ques)
    state["messages"] += [HumanMessage(content=ask_user)]

    # Invoke the deal_chain to extract structured deal data
    response = deal_chain.invoke({"messages": state["messages"]})
    tool_data = response.tool_calls[0]["args"]
    print("🧠 Deal Agent Output:", tool_data["message"])

    user_price = tool_data.get("user_price")
    is_deal = tool_data.get("isDeal", False)
    message = tool_data.get("message", "")

    if user_price == -1:
        invalid_msg = "It seems like your input wasn’t clear. Could you please specify a valid price you'd be comfortable with?"
        state["messages"] += [AIMessage(content=invalid_msg)]
        state["final_response"] = invalid_msg
        state["isDeal"] = False
        state["agreed_price"] = -1
        return state

    if is_deal:
        state["agreed_price"] = user_price
        state["isDeal"] = True
        state["final_response"] = message
        state["messages"] += [AIMessage(content=message)]
        return state

    if user_price <= acceptable_limit and user_price != -1:
        agree_msg = (
            f"Sure, we can proceed with ₹{user_price}. Looking forward to working together!"
        )
        state["agreed_price"] = user_price
        state["isDeal"] = True
        state["final_response"] = agree_msg
        state["messages"] += [AIMessage(content=agree_msg)]
        return state

    # User asked more than 10%
    max_budget_msg = (
        f"We truly value your work, but our max budget for this campaign is capped at ₹{init_budget*1.10}. "
        "Would you be open to proceeding with this?"
    )
    state["messages"] += [AIMessage(content=max_budget_msg)]

    followup_response = input(max_budget_msg)
    state["messages"] += [HumanMessage(content=followup_response)]

    followup_result = deal_chain.invoke({"messages": state["messages"]})
    followup_data = followup_result.tool_calls[0]["args"]

    user_price = followup_data.get("user_price")

    if user_price == -1:
        invalid_msg = "It seems like your input wasn’t clear. Could you please specify a valid price you'd be comfortable with?"
        state["messages"] += [AIMessage(content=invalid_msg)]
        state["final_response"] = invalid_msg
        state["isDeal"] = False
        state["agreed_price"] = -1
        return state

    if followup_data.get("isDeal"):
        state["agreed_price"] = init_budget
        state["isDeal"] = True
        state["final_response"] = followup_data.get("message", "Great! We're proceeding with the original budget.")

    else:
        state["agreed_price"] = -1
        state["isDeal"] = False
        state["final_response"] = followup_data.get("message", "Sad to miss this opportunity, hope to work together soon! You can restart the conversation if you think its a mistake from your mailbox")

    state["messages"] += [AIMessage(content=state["final_response"])]
    return state

graph.add_node(GREET_INTRO, greet_node)
graph.add_node(CAMPAIGN_QUERY, campaign_query)
graph.add_node(BUDGET_NEGOTIATOR, budget_negotiator)

graph.add_conditional_edges(GREET_INTRO, checkBudgetInterest)

graph.add_edge(CAMPAIGN_QUERY, BUDGET_NEGOTIATOR)

graph.set_entry_point(GREET_INTRO)

app = graph.compile()

print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

# Fixed state initialization - start with empty messages, they'll be created in greet_node
state = {
    "final_response": "",
    "agreed_price": 0,
    "isDeal": False,
    "init_budget": 300,
    "messages": []
}

# Execute the graph
try:
    response = app.invoke(state)
    print("Final response:", response)
except Exception as e:
    print(f"Error executing graph: {e}")