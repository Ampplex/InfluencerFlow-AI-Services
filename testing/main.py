# chatbot_with_gemini.py
# Enhanced version with Google Gemini 2.0 Flash via LangChain

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import os
from flask import Flask, request, send_from_directory
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from testing.tts_utils import generate_audio
import time
from threading import Thread
from dotenv import load_dotenv

# Configuration
TWILIO_ACCOUNT_SID = "AC03c65a8e150151f571e578833045f196"
TWILIO_AUTH_TOKEN = "93549853288bc73a803b449b0f498dea"
TWILIO_PHONE_NUMBER = "+12183082097"
YOUR_PHONE_NUMBER = "+918668959768"
ELEVEN_LABS_API_KEY = "sk_bd95e1799e293b4cd714c5b264579501ae5dffc6dc249791"
DOMAIN = "https://b0a8-103-133-158-92.ngrok-free.app"

load_dotenv()

# Initialize Gemini 2.0 Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.8,
    max_tokens=150,
    timeout=10,
    max_retries=2,
)

app = Flask(__name__)
conversations = {}

@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory("audio", filename, mimetype='audio/mpeg')

@app.route("/twiml", methods=["POST"])
def twiml():
    try:
        caller = request.form.get('From', 'unknown')
        
        if caller not in conversations:
            conversations[caller] = []
        
        welcome_message = "Hello! I'm your AI assistant powered by Gemini. I can help you with questions, have conversations, brainstorm ideas, or just chat. What would you like to talk about today?"
        audio_file = generate_audio(welcome_message)
        audio_url = f"{DOMAIN}/audio/{audio_file}"
        
        response = VoiceResponse()
        response.play(audio_url)
        
        gather = Gather(
            input='speech',
            timeout=8,
            speech_timeout='auto',
            action=f'{DOMAIN}/process_speech',
            method='POST',
            language='en-US'
        )
        gather.pause(length=1)
        response.append(gather)
        
        response.say("I didn't hear anything. Feel free to call back anytime!")
        response.hangup()
        
        return str(response)
        
    except Exception as e:
        print(f"Error in twiml route: {e}")
        response = VoiceResponse()
        response.say("Sorry, there was a technical issue. Please try again.")
        return str(response)

@app.route("/process_speech", methods=["POST"])
def process_speech():
    try:
        caller = request.form.get('From', 'unknown')
        speech_result = request.form.get('SpeechResult', '').strip()
        confidence = float(request.form.get('Confidence', 0))
        
        print(f"Speech from {caller}: '{speech_result}' (confidence: {confidence:.2f})")
        
        if not speech_result or confidence < 0.5:
            return handle_unclear_speech()
        
        # Manage conversation history
        if caller not in conversations:
            conversations[caller] = []
        
        conversations[caller].append(HumanMessage(content=speech_result))
        
        # Keep conversation history manageable (last 10 exchanges)
        if len(conversations[caller]) > 20:
            conversations[caller] = conversations[caller][-10:]
        
        # Generate intelligent response using Gemini
        ai_response = generate_gemini_response(conversations[caller])
        conversations[caller].append(AIMessage(content=ai_response))
        
        # Convert to audio
        audio_file = generate_audio(ai_response)
        audio_url = f"{DOMAIN}/audio/{audio_file}"
        
        response = VoiceResponse()
        response.play(audio_url)
        
        # Check if user wants to end conversation
        if is_conversation_ending(speech_result, ai_response):
            response.say("Thanks for the wonderful conversation!")
            response.hangup()
        else:
            # Continue conversation
            gather = Gather(
                input='speech',
                timeout=12,
                speech_timeout='auto',
                action=f'{DOMAIN}/process_speech',
                method='POST',
                language='en-US'
            )
            gather.pause(length=1)
            response.append(gather)
            
            response.say("It was great chatting with you. Have an amazing day!")
            response.hangup()
        
        return str(response)
        
    except Exception as e:
        print(f"Error processing speech: {e}")
        return handle_error()

def generate_gemini_response(conversation_history):
    """Generate intelligent responses using Gemini 2.0 Flash"""
    try:
        # Create system message for context
        system_prompt = """You are a friendly, helpful AI voice assistant powered by Gemini. 
        Keep responses conversational, engaging, and under 100 words since this is a voice conversation. 
        Be natural, personable, and helpful. You can chat, answer questions, help with ideas, 
        provide information, or just have a friendly conversation.
        
        If someone wants to end the call, be gracious and brief.
        Speak in a conversational tone as if you're talking to a friend."""
        
        # Prepare messages for Gemini
        messages = [SystemMessage(content=system_prompt)]
        messages.extend(conversation_history)
        
        # Generate response
        response = llm.invoke(messages)
        
        # Extract text content
        if hasattr(response, 'content'):
            return response.content.strip()
        else:
            return str(response).strip()
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return generate_fallback_response(conversation_history)

def generate_fallback_response(conversation_history):
    """Fallback responses when Gemini is unavailable"""
    if not conversation_history:
        return "I'm here to help! What would you like to talk about?"
    
    # Get the last human message
    last_message = ""
    for msg in reversed(conversation_history):
        if isinstance(msg, HumanMessage):
            last_message = msg.content.lower()
            break
    
    responses = {
        "hello": "Hello there! It's wonderful to hear from you. How are you doing today?",
        "how are you": "I'm doing great, thank you for asking! How about you?",
        "weather": "I don't have access to current weather data, but I'd love to chat about something else!",
        "help": "I'm here to chat and help however I can. What's on your mind?",
        "bye": "It was lovely talking with you! Have a wonderful day!",
        "thank": "You're very welcome! Is there anything else I can help you with?",
        "what can you do": "I can chat about almost anything! Ask me questions, brainstorm ideas, or just have a friendly conversation.",
        "joke": "Here's one for you: Why don't scientists trust atoms? Because they make up everything!",
    }
    
    for keyword, response in responses.items():
        if keyword in last_message:
            return response
    
    return "That's really interesting! I'd love to hear more about that. What else would you like to discuss?"

def handle_unclear_speech():
    """Handle unclear or low-confidence speech"""
    response = VoiceResponse()
    response.say("I didn't quite catch that. Could you please speak a bit more clearly?")
    
    gather = Gather(
        input='speech',
        timeout=8,
        speech_timeout='auto',
        action=f'{DOMAIN}/process_speech',
        method='POST'
    )
    gather.pause(length=1)
    response.append(gather)
    
    response.say("No worries! Feel free to call back anytime.")
    response.hangup()
    return str(response)

def handle_error():
    """Handle processing errors gracefully"""
    response = VoiceResponse()
    response.say("I'm having a small technical hiccup. Let me try again.")
    
    gather = Gather(
        input='speech',
        timeout=5,
        speech_timeout='auto',
        action=f'{DOMAIN}/process_speech',
        method='POST'
    )
    gather.say("Please go ahead and speak.")
    response.append(gather)
    
    response.say("Thanks for your patience. Have a great day!")
    response.hangup()
    return str(response)

def is_conversation_ending(user_input, ai_response):
    """Determine if conversation should end"""
    end_phrases = [
        "bye", "goodbye", "see you", "talk later", "gotta go", 
        "have to go", "end call", "hang up", "thanks for", "that's all"
    ]
    
    user_lower = user_input.lower()
    ai_lower = ai_response.lower()
    
    return (any(phrase in user_lower for phrase in end_phrases) or 
            any(phrase in ai_lower for phrase in ["goodbye", "have a great day", "bye"]))

def start_call():
    """Initiate the chatbot call"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            to=YOUR_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{DOMAIN}/twiml"
        )
        print(f"🤖 Gemini AI Chatbot call started: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"Error starting call: {e}")
        return None

def run_flask():
    """Run Flask app"""
    app.run(host='0.0.0.0', port=8080, debug=False)

def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        test_message = [SystemMessage(content="You are a helpful assistant."), 
                       HumanMessage(content="Say hello")]
        response = llm.invoke(test_message)
        print(f"✅ Gemini connection successful: {response.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False

if __name__ == "__main__":
    os.makedirs("audio", exist_ok=True)
    
    # Test Gemini connection first
    print("🧪 Testing Gemini 2.0 Flash connection...")
    if not test_gemini_connection():
        print("⚠️  Gemini connection failed. The bot will use fallback responses.")
        print("Make sure to set your GOOGLE_API_KEY correctly.")
    
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("🚀 Starting Gemini-powered Voice Chatbot...")
    time.sleep(3)
    
    print("📞 Initiating intelligent voice conversation with Gemini 2.0 Flash...")
    start_call()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Gemini Chatbot shutting down...")