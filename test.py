import ollama

print("initiating streaming chat...")

response = ollama.chat(
    model="deepseek-r1",
    options={
        "temperature": 0.2,  # consistent grading
    },
    messages=[{"role": "user", "content": "Hello, Ollama!"}],
    stream=True
)

print("streaming response:")

for chunk in response:
    print(chunk['message']['content'], end='', flush=True)
