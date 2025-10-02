# groq_chat.py
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
class GROQ:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("Groq_API"))

    def chat_with_groq(self,prompt: str, model: str = "qwen/qwen3-32b",):
        """Send a chat prompt to the Groq API and stream the response."""
        completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_completion_tokens=1024,
            top_p=0.95,
            stream=True,
        )

        response = []
        for chunk in completion:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            response.append(delta)
            print()  # for clean newline
        return "".join(response)

