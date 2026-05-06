import os
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def transcribe_audio(file_path):
    """Voice note ko sun kar usay English text mein convert karta hai."""
    try:
        with open(file_path, "rb") as file:
            # Direct file bhej rahe hain taake path ka masla na aaye
            translation = client.audio.translations.create(
              file=file,
              model="whisper-large-v3"
            )
            # Response mein se sirf text nikal kar wapas bhej do
            return translation.text
            
    except Exception as e:
        print(f"Whisper Error: {e}")
        return "Audio transcribe nahi ho saki."