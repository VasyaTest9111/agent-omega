import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._model = None

    def _get_model(self):
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=(
                    "Ти — AI-асистент з доступом до GitHub репозиторіїв. "
                    "Відповідай коротко і по суті. Якщо є контекст GitHub — використовуй його. "
                    "Пиши українською якщо питання українською, інакше мовою запиту."
                ),
            )
        return self._model

    def ask(self, user_message: str, github_context: Optional[str] = None, history: Optional[List[str]] = None) -> str:
        if not self.api_key:
            return "❌ GEMINI_API_KEY не встановлено"

        try:
            model = self._get_model()
            parts = []
            if history:
                parts.append("Попередні репліки цього чату:\n" + "\n\n".join(history))
            if github_context:
                parts.append(f"Контекст GitHub:\n{github_context}")
            parts.append(f"Запит: {user_message}")
            prompt = "\n\n".join(parts)

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"❌ Помилка Gemini: {e}"
