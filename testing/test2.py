from typing import List, Literal, Dict, Any, Optional
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from datetime import datetime
import os

load_dotenv(verbose=True)

# Enhanced Schema definitions
class Greet_Intro_Response(BaseModel):
    greet_intro: str = Field(description="Greet the user and share the short brand intro and campaign details")

class CheckBudgetInterest(BaseModel):
    interest_response: bool = Field(description="If the user said yes or gave positive signs to know the budget then strictly assign boolean interest_response True or else False")

class BudgetResponseAnalysis(BaseModel):
    """Analyze user's response to budget offer"""
    response_type: Literal["accept", "counter_offer", "reject", "unclear"] = Field(
        description="Classify the response: 'accept' if they agree, 'counter_offer' if asking for more money, 'reject' if declining, 'unclear' if ambiguous"
    )
    requested_amount: int = Field(
        description="Amount requested by user in dollars. 0 if not specified or accepting current offer",
        default=0
    )
    reasoning: str = Field(description="Brief explanation of why this classification was chosen")

class NegotiationResponse(BaseModel):
    response_message: str = Field(description="Professional response to the influencer's request")
    final_offer: int = Field(description="Final offer amount in dollars")
    continue_negotiation: bool = Field(description="True if negotiation should continue, False if ending")

# Negotiation State Management
class NegotiationState:
    def __init__(self, init_budget: int = 300):
        self.final_response = ""
        self.agreed_price = 0
        self.isDeal = False
        self.init_budget = init_budget
        self.max_budget = int(init_budget * 1.10)  # 10% increase
        self.current_offer = 0
        self.negotiation_round = 0
        self.messages: List[BaseMessage] = []
        self.current_step = ""
        self.last_user_response = ""
        self.response_type = ""
        self.requested_amount = 0
        self.is_final_offer = False

# Configuration
BRAND_CONFIG = {
    "brand": "Meta",
    "brand_description": "Social Media tech giant",
    "campaign": "Meta Developer Conference",
    "campaign_description": "Post 3 to 4 thumbnails for the tech event",
    "influencer_name": "Ankesh Kumar"
}

def get_time_greeting():
    """Get appropriate greeting based on current time"""
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def setup_llm():
    """Initialize the LLM with proper configuration"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2  # Lower temperature for more consistent responses
    )

# Custom Tools for Negotiation Steps
class GreetingTool(BaseTool):
    name = "greeting_tool"
    description = "Generate greeting and campaign introduction"
    state: NegotiationState = Field(default_factory=NegotiationState)
    
    def _run(self, user_input: str = "") -> str:
        try:
            llm = setup_llm()
            converted_greet_tool = convert_to_openai_tool(Greet_Intro_Response)
            
            greet_prompt_template = ChatPromptTemplate.from_messages([
                ("system", 
                 """You are a brand representative for {brand}, which is described as: {brand_description}.
                 You are looking for influencers for your campaign: {campaign}.
                 Campaign description: {campaign_description}
                 
                 Your tasks:
                 1. Greet the influencer ({influencer_name}) with a {time_greeting}
                 2. Provide a brief introduction of your brand
                 3. Explain the campaign details clearly and enthusiastically
                 
                 Keep the tone professional yet friendly, and make the campaign sound exciting and worthwhile.
                 """),
                ("user", "{user_input}")
            ]).partial(
                time_greeting=get_time_greeting(),
                **BRAND_CONFIG
            )
            
            greet_chain = (
                greet_prompt_template 
                | llm.bind_tools(
                    tools=[converted_greet_tool],
                    tool_choice="Greet_Intro_Response"
                )
            )
            
            response = greet_chain.invoke({"user_input": user_input or "Hi, I'm interested in learning about your campaign"})
            
            if response.tool_calls:
                greet_content = response.tool_calls[0]["args"]["greet_intro"]
                self.state.final_response = greet_content
                self.state.current_step = "greeting"
                return greet_content
            else:
                fallback_response = f"{get_time_greeting()} {BRAND_CONFIG['influencer_name']}! I'm reaching out from {BRAND_CONFIG['brand']} about our {BRAND_CONFIG['campaign']} campaign."
                self.state.final_response = fallback_response
                return fallback_response
                
        except Exception as e:
            print(f"❌ Error in greeting_tool: {str(e)}")
            return "Hello! I'd like to discuss a campaign opportunity with you."

class BudgetAnalysisTool(BaseTool):
    name = "budget_analysis_tool"
    description = "Analyze user's response to budget offers"
    state: NegotiationState = Field(default_factory=NegotiationState)
    
    def _run(self, user_response: str) -> Dict[str, Any]:
        try:
            llm = setup_llm()
            converted_analysis_tool = convert_to_openai_tool(BudgetResponseAnalysis)
            
            analysis_prompt_template = ChatPromptTemplate.from_messages([
                ("system", 
                 """You are an expert at analyzing negotiation responses. Analyze the user's response to a budget offer.
                 
                 Current context:
                 - Budget offered: ${current_budget}
                 - Maximum possible budget: ${max_budget}
                 
                 Classify their response as:
                 - "accept": They agree to the current offer (words like "ok", "fine", "deal", "agreed", "sounds good")
                 - "counter_offer": They want more money or negotiate (mentions specific amounts, "more", "higher", "can you do X")
                 - "reject": They decline the offer entirely ("no", "not interested", "too low", "can't do it")
                 - "unclear": Response is ambiguous or doesn't clearly indicate their position
                 
                 Extract any monetary amount they mention. Look for:
                 - Direct amounts: "$400", "400 dollars", "four hundred"
                 - Percentage increases: "20% more", "50% higher"
                 - Range requests: "between X and Y"
                 
                 Be very precise in your classification.
                 """),
                ("user", "User response: {user_response}")
            ])
            
            analysis_chain = (
                analysis_prompt_template
                | llm.bind_tools(
                    tools=[converted_analysis_tool],
                    tool_choice="BudgetResponseAnalysis"
                )
            )
            
            analysis_context = {
                "user_response": user_response,
                "current_budget": self.state.current_offer,
                "max_budget": self.state.max_budget
            }
            
            analysis_response = analysis_chain.invoke(analysis_context)
            
            if analysis_response.tool_calls:
                analysis = analysis_response.tool_calls[0]["args"]
                
                self.state.response_type = analysis["response_type"]
                self.state.requested_amount = analysis.get("requested_amount", 0)
                self.state.last_user_response = user_response
                
                return {
                    "response_type": analysis["response_type"],
                    "requested_amount": analysis.get("requested_amount", 0),
                    "reasoning": analysis.get("reasoning", "")
                }
            else:
                return {
                    "response_type": "unclear",
                    "requested_amount": 0,
                    "reasoning": "Could not analyze response"
                }
                
        except Exception as e:
            print(f"❌ Error in budget_analysis_tool: {str(e)}")
            return {
                "response_type": "unclear",
                "requested_amount": 0,
                "reasoning": f"Error: {str(e)}"
            }

class NegotiationTool(BaseTool):
    name = "negotiation_tool"
    description = "Handle negotiation responses and counter-offers"
    state: NegotiationState = Field(default_factory=NegotiationState)
    
    def _run(self, analysis_result: Dict[str, Any]) -> str:
        try:
            llm = setup_llm()
            converted_negotiation_tool = convert_to_openai_tool(NegotiationResponse)
            
            response_type = analysis_result.get("response_type", "unclear")
            requested_amount = analysis_result.get("requested_amount", 0)
            
            if response_type == "accept":
                self.state.isDeal = True
                self.state.agreed_price = self.state.current_offer
                return f"Excellent! Deal confirmed at ${self.state.current_offer}. Looking forward to working with you!"
            
            elif response_type == "reject":
                self.state.isDeal = False
                return "I understand this might not be the right fit. Thank you for your time!"
            
            elif response_type == "counter_offer":
                # Handle counter offer
                if requested_amount > self.state.max_budget:
                    # Final offer at max budget
                    final_message = f"I understand you're looking for ${requested_amount}, but our absolute maximum budget for this campaign is ${self.state.max_budget}. This is the highest we can go. Would you be interested in proceeding at ${self.state.max_budget}?"
                    self.state.current_offer = self.state.max_budget
                    self.state.is_final_offer = True
                    return final_message
                else:
                    # Negotiate within budget
                    negotiation_prompt_template = ChatPromptTemplate.from_messages([
                        ("system", 
                         """You are a brand representative for {brand} handling budget negotiations.
                         
                         CONTEXT:
                         - Campaign: {campaign}
                         - Initial budget: ${init_budget}
                         - Maximum budget (absolute limit): ${max_budget}
                         - Current offer: ${current_offer}
                         - User requested: ${requested_amount}
                         - Negotiation round: {round}
                         
                         NEGOTIATION RULES:
                         1. If requested amount <= max_budget: Offer the requested amount and end negotiation
                         2. If requested amount > max_budget: Offer max_budget as final offer
                         3. Always be professional and emphasize campaign value
                         4. If this is the final offer (at max_budget), clearly state it's the maximum possible
                         5. After 3 rounds, start pushing for closure
                         
                         RESPONSE GUIDELINES:
                         - Be firm but friendly
                         - Highlight campaign benefits (Meta brand exposure, developer community reach)
                         - If offering max budget, clearly state this is the absolute maximum
                         - Keep responses concise and professional
                         """),
                        ("user", "Handle this negotiation scenario")
                    ]).partial(**BRAND_CONFIG)
                    
                    negotiation_chain = (
                        negotiation_prompt_template
                        | llm.bind_tools(
                            tools=[converted_negotiation_tool],
                            tool_choice="NegotiationResponse"
                        )
                    )
                    
                    negotiation_context = {
                        "init_budget": self.state.init_budget,
                        "max_budget": self.state.max_budget,
                        "current_offer": self.state.current_offer,
                        "requested_amount": requested_amount,
                        "round": self.state.negotiation_round
                    }
                    
                    negotiation_response = negotiation_chain.invoke(negotiation_context)
                    
                    if negotiation_response.tool_calls:
                        result = negotiation_response.tool_calls[0]["args"]
                        
                        response_message = result["response_message"]
                        final_offer = min(result.get("final_offer", requested_amount), self.state.max_budget)
                        
                        self.state.current_offer = final_offer
                        self.state.negotiation_round += 1
                        
                        if final_offer == self.state.max_budget:
                            return f"{response_message} Our final offer is ${final_offer} - this is the maximum we can allocate for this campaign."
                        else:
                            return f"{response_message} We can offer ${final_offer}."
                    else:
                        self.state.current_offer = min(requested_amount, self.state.max_budget)
                        return f"We can work with ${self.state.current_offer} for this campaign."
            
            else:  # unclear
                return "Could you please clarify your thoughts on the budget? Are you interested in proceeding with the offer?"
                
        except Exception as e:
            print(f"❌ Error in negotiation_tool: {str(e)}")
            return "Let me see what we can do within our budget constraints."

# Main Negotiation Agent Class
class NegotiationAgent:
    def __init__(self, init_budget: int = 300):
        self.state = NegotiationState(init_budget)
        self.llm = setup_llm()
        
        # Initialize tools with shared state
        self.greeting_tool = GreetingTool()
        self.greeting_tool.state = self.state
        
        self.budget_analysis_tool = BudgetAnalysisTool()
        self.budget_analysis_tool.state = self.state
        
        self.negotiation_tool = NegotiationTool()
        self.negotiation_tool.state = self.state
        
        self.tools = [self.greeting_tool, self.budget_analysis_tool, self.negotiation_tool]
        
        # Create agent prompt
        self.agent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional brand representative for {brand} handling influencer negotiations.
            
            Your role is to:
            1. Greet influencers and introduce the campaign
            2. Present budget offers professionally
            3. Analyze responses and negotiate within budget limits
            4. Close deals or politely decline when necessary
            
            Current Campaign: {campaign}
            Budget Range: ${init_budget} - ${max_budget}
            
            Use the available tools to handle different stages of negotiation:
            - greeting_tool: For initial introductions
            - budget_analysis_tool: To analyze user responses to budget offers
            - negotiation_tool: To handle counter-offers and negotiations
            
            Always maintain professionalism and focus on mutual benefit.
            """.format(**BRAND_CONFIG, init_budget=self.state.init_budget, max_budget=self.state.max_budget)),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])
        
        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.agent_prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def start_negotiation(self):
        """Start the negotiation process"""
        print("🔄 Advanced Negotiation System")
        print("="*60)
        print(f"💰 Budget Parameters:")
        print(f"   Initial Budget: ${self.state.init_budget}")
        print(f"   Maximum Budget: ${self.state.max_budget} (10% increase)")
        print("="*60)
        
        # Step 1: Greeting
        greeting_response = self.greeting_tool._run("Hi, I'm interested in your campaign")
        print(f"\n📢 Brand Representative: {greeting_response}")
        
        # Step 2: Check interest in budget
        interest = input("\n❓ Would you like to discuss the budget details? (yes/no): ").strip().lower()
        
        if interest not in ['yes', 'y', 'sure', 'ok', 'okay']:
            print("❌ Not interested in budget discussion. Thank you for your time!")
            return
        
        # Step 3: Present initial budget
        self.state.current_offer = self.state.init_budget
        budget_message = f"💰 Our budget for the {BRAND_CONFIG['campaign']} campaign is ${self.state.init_budget}. This covers all the deliverables we discussed. What are your thoughts on this?"
        print(f"\n🤝 Brand Representative: {budget_message}")
        
        # Step 4: Start negotiation loop
        max_rounds = 5
        current_round = 0
        
        while current_round < max_rounds and not self.state.isDeal:
            user_response = input("\n💬 Your response: ").strip()
            
            if not user_response:
                user_response = "Let me think about it"
            
            # Analyze response
            analysis = self.budget_analysis_tool._run(user_response)
            print(f"\n🔍 Analysis: {analysis['response_type']} - {analysis['reasoning']}")
            
            # Handle negotiation
            negotiation_response = self.negotiation_tool._run(analysis)
            print(f"\n🤝 Brand Representative: {negotiation_response}")
            
            # Check if deal is done
            if self.state.isDeal or self.state.response_type in ["accept", "reject"]:
                break
            
            # Check if final offer was made
            if self.state.is_final_offer:
                final_user_response = input("\n💬 Your final response: ").strip()
                final_analysis = self.budget_analysis_tool._run(final_user_response)
                
                if final_analysis['response_type'] == "accept":
                    self.state.isDeal = True
                    self.state.agreed_price = self.state.current_offer
                    print("\n✅ Final offer accepted! Deal confirmed!")
                else:
                    print("\n❌ Final offer declined. Thank you for your time!")
                break
            
            current_round += 1
        
        # Print final results
        self.print_results()
    
    def print_results(self):
        """Print final negotiation results"""
        print("\n" + "="*60)
        print("🏁 NEGOTIATION RESULTS")
        print("="*60)
        print(f"🤝 Deal Status: {'✅ DEAL CLOSED' if self.state.isDeal else '❌ NO DEAL'}")
        
        if self.state.isDeal:
            agreed_price = self.state.agreed_price
            savings = self.state.max_budget - agreed_price
            print(f"💰 Agreed Price: ${agreed_price}")
            print(f"💸 Budget Saved: ${savings}")
            print(f"📊 Budget Utilization: {(agreed_price/self.state.max_budget)*100:.1f}%")
        
        print(f"🔄 Negotiation Rounds: {self.state.negotiation_round}")
        print(f"📝 Final Status: {self.state.current_step}")

def main():
    """Main execution function"""
    try:
        # Initialize and start negotiation
        agent = NegotiationAgent(init_budget=300)
        agent.start_negotiation()
        
    except Exception as e:
        print(f"❌ System Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()