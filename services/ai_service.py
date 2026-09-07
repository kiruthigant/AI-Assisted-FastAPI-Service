import os
import json
from pydantic import ValidationError
import openai
import google.generativeai as genai
from schemas import FeedbackAnalysis

class AIServiceException(Exception):
    pass

class LLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not set.")
            self.client = openai.OpenAI(api_key=api_key)
        elif self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            raise ValueError("Invalid LLM_PROVIDER specified. Use 'openai' or 'gemini'.")

    def get_system_prompt(self):
        return (
            "You are an expert customer feedback analyzer. Extract the sentiment (POSITIVE, NEGATIVE, NEUTRAL), "
            "a 1-sentence summary, an urgency_score (1-5), and a list of action_items from the provided feedback.\n"
            "You MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",\n'
            '  "summary": "string",\n'
            '  "urgency_score": int,\n'
            '  "action_items": ["item1", "item2"]\n'
            "}"
        )

    def analyze_feedback(self, text: str) -> FeedbackAnalysis:
        prompt = f"Feedback: {text}\nAnalyze this feedback."
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                raw_result = response.choices[0].message.content
            elif self.provider == "gemini":
                full_prompt = self.get_system_prompt() + "\n\n" + prompt
                response = self.model.generate_content(full_prompt)
                raw_result = response.text
                
            # Cleanup for markdown formatting if present
            raw_result = raw_result.strip()
            if raw_result.startswith("```json"):
                raw_result = raw_result[7:]
            if raw_result.startswith("```"):
                raw_result = raw_result[3:]
            if raw_result.endswith("```"):
                raw_result = raw_result[:-3]
            raw_result = raw_result.strip()

            parsed_data = json.loads(raw_result)
            return FeedbackAnalysis(**parsed_data)
        except json.JSONDecodeError:
            raise AIServiceException("LLM returned invalid JSON.")
        except ValidationError as e:
            raise AIServiceException(f"LLM output failed validation: {str(e)}")
        except Exception as e:
            raise AIServiceException(f"LLM Service Error: {str(e)}")
