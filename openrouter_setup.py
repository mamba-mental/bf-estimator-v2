from openrouter import Client

# Replace "sk-or-..." with your actual API key from OpenRouter
client = Client(
    api_key="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",  
    default_model="anthropic/claude-3.7-sonnet",  # Default model to use
    fallbacks=["deepseek/deepseek-chat-v3-0324", "mistralai/codestral-2501"]  # Backup models if needed
)

# Example request to test connection
response = client.chat.completions.create(
    model="anthropic/claude-3.7-sonnet",
    messages=[{"role": "user", "content": "What is the meaning of life?"}]
)

print(response)
