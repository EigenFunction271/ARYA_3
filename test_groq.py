import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Test Groq directly
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say hello!"
        }
    ],
    model="mixtral-8x7b-32768",
)

print(chat_completion.choices[0].message.content) 