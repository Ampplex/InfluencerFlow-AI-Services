# tts_utils.py
import requests
import uuid
import os

ELEVEN_API_KEY = "sk_bd95e1799e293b4cd714c5b264579501ae5dffc6dc249791"
ELEVEN_VOICE_ID = "3Th96YoTP1kEKxJroYo1"

def generate_audio(text):
    """
    Generate audio from text using ElevenLabs API
    
    Args:
        text (str): Text to convert to speech
        
    Returns:
        str: Filename of the generated audio file
        
    Raises:
        Exception: If the API request fails
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            print(f"ElevenLabs API error: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Failed to fetch audio from ElevenLabs: {response.status_code}")
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.mp3"
        path = os.path.join("audio", filename)
        
        # Save audio file
        with open(path, "wb") as f:
            f.write(response.content)
        
        print(f"Audio file generated: {filename}")
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise Exception(f"Network error when calling ElevenLabs API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def get_available_voices():
    """
    Get list of available voices from ElevenLabs API
    
    Returns:
        list: List of available voices
    """
    url = "https://api.elevenlabs.io/v1/voices"
    
    headers = {
        "xi-api-key": ELEVEN_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            return voices.get('voices', [])
        else:
            print(f"Error fetching voices: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []

# Common voice IDs for reference:
VOICE_IDS = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Drew": "29vD33N1CtxCmqQRPOHJ",
    "Clyde": "2EiwWnXFnvU5JabPnv8n",
    "Paul": "5Q0t7uMcjvnagumLfvZi",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Dave": "CYw3kZ02Hs0563khs1Fj",
    "Fin": "D38z5RcWu1voky8WS1ja",
    "Sarah": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Thomas": "GBv7mTt0atIp3Br8iCZE",
    "Emily": "LcfcDJNUP1GQjkzn1xUU",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Callum": "N2lVS1w4EtoT3dr4eOWO",
    "Patrick": "ODq5zmih8GrVes37Dizd",
    "Harry": "SOYHLrjzK2X1ezoPC6cr",
    "Liam": "TX3LPaxmHKxFdv7VOQHJ",
    "Dorothy": "ThT5KcBeYPX3keUQqHPh",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Charlotte": "XB0fDUnXU5powFXDhCwa",
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Matilda": "XrExE9yKIg1WjnnlVkGX",
    "James": "ZQe5CZNOzWyzPSCn5a3c",
    "Joseph": "Zlb1dXrM653N07WRdFW3",
    "Jeremy": "bVMeCyTHy58xNoL34h3p",
    "Michael": "flq6f7yk4E4fJM5XTYuZ",
    "Ethan": "g5CIjZEefAph4nQFvHAz",
    "Chris": "iP95p4xoKVk53GoZ742B",
    "Gigi": "jBpfuIE2acCO8z3wKNLl",
    "Freya": "jsCqWAovK2LkecY7zXl4",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Grace": "oWAxZDx7w5VEj9dCyTzz",
    "Daniel": "onwK4e9ZLuTAKqWW03F9",
    "Lily": "pFZP5JQG7iQjIQuC4Bku",
    "Serena": "pMsXgVXv3BLzUgSXRplE",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Nicole": "piTKgcLEGmPE4e6mEKli",
    "Jessie": "t0jbNlBVZ17f02VDIeMI",
    "Ryan": "wViXBPUzp2ZZixB1xQuM",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
    "Glinda": "z9fAnlkpzviPz146aGWa",
    "Giovanni": "zcAOhNBS3c14rBihAFp1",
    "Mimi": "zrHiDhphv9ZnVXBqCLjz"
}