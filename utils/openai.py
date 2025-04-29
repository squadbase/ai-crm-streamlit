from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(".env")

openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
