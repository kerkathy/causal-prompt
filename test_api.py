import os
import openai

api_key = os.getenv("PARATERA_API_KEY")
base_url = os.getenv("PARATERA_BASE_URL", "https://llmapi.paratera.com/v1/")
model_id = "DeepSeek-R1-Distill-Qwen-7B"

client = openai.OpenAI(api_key=api_key, base_url=base_url)

response = client.chat.completions.create(
    model=model_id,  # model to send to the proxy
    messages=[
        {
            "role": "user",
            "content": "Hello world"        
        }
    ]
)
print(response.choices[0].message.content)