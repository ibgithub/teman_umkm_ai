from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)


def ask_qwen(prompt: str) -> str:
    response = client.chat.completions.create(
        model="qwen2.5:7b",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()