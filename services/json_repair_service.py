import json
import re


class JsonRepairService:

    @staticmethod
    def repair(raw_response: str) -> dict:

        if not raw_response:
            raise ValueError("LLM returned an empty response.")

        text = raw_response.strip()

        # -----------------------------------------
        # Remove Markdown Code Fences
        # -----------------------------------------

        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r"^```", "", text, flags=re.MULTILINE)
        text = re.sub(r"```$", "", text, flags=re.MULTILINE)

        text = text.strip()

        # -----------------------------------------
        # Extract JSON Object
        # -----------------------------------------

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found in LLM response.")

        text = text[start : end + 1]

        # -----------------------------------------
        # Remove Trailing Commas
        # -----------------------------------------

        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        # -----------------------------------------
        # Parse JSON
        # -----------------------------------------

        try:
            return json.loads(text)

        except json.JSONDecodeError as e:

            raise ValueError(f"JSON parsing failed.\n\n{e}\n\n{text}")
