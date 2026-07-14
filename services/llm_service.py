import ollama


class LLMService:

    MODEL = "qwen3.5:9b"

    @staticmethod
    def generate(prompt: str) -> str:

        print("\n==============================")
        print("Calling Local LLM...")
        print("==============================\n")

        response = ollama.chat(
            model=LLMService.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
                "num_ctx": 32768,
            },
        )

        content = response["message"]["content"]

        print("LLM Response Received.\n")

        return content.strip()
