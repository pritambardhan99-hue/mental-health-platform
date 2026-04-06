# ch.py

import requests


class OpenRouterChatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        # Store conversation history (OpenAI format)
        self.history = []

        # Model
        self.model = "openai/gpt-oss-20b:free"
        # 🔥 Recommended instead:
        # self.model = "openrouter/free"

    def ask(self, user_input):
        try:
            # Add user message
            self.history.append({
                "role": "user",
                "content": user_input
            })

            payload = {
                "model": self.model,
                "messages": self.history
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.url, headers=headers, json=payload)

            # Debug (optional)
            # print(response.status_code, response.text)

            if response.status_code != 200:
                return f"❌ API Error: {response.text}"

            data = response.json()

            if "choices" not in data:
                return "❌ Invalid response from API"

            bot_reply = data["choices"][0]["message"]["content"]

            # Save bot reply
            self.history.append({
                "role": "assistant",
                "content": bot_reply
            })

            return bot_reply

        except Exception as e:
            return f"❌ Error: {str(e)}"


def main():
    API_KEY = "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"  # 🔑 PUT YOUR KEY HERE

    bot = OpenRouterChatbot(API_KEY)

    print("🤖 OpenRouter Chatbot (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye 👋")
            break

        reply = bot.ask(user_input)
        print("Bot:", reply)


if __name__ == "__main__":
    main()