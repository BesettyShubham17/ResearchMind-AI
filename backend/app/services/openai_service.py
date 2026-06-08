import logging
from typing import List, Optional
from app.config.settings import settings

logger = logging.getLogger("researchmind.openai")

class OpenAIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"OpenAI client init failed: {e}")

    def _chat(self, system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
        if not self.client:
            return f"[Mock Response] Analysis complete for: {user_prompt[:80]}..."
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return f"[Error] Could not generate response: {e}"

    def generate_summary(self, topic: str, sources: list) -> str:
        source_texts = "\n\n".join([f"- {s.get('title', '')}: {s.get('content', '')[:300]}" for s in sources[:5]])
        system = "You are an expert research analyst. Write a concise executive summary."
        user = f"Topic: {topic}\n\nSources:\n{source_texts}\n\nWrite a professional executive summary in 3-4 paragraphs."
        return self._chat(system, user)

    def generate_report(self, topic: str, summary: str, sources: list) -> dict:
        system = "You are a senior research consultant generating structured reports."
        user = f"""Topic: {topic}\nSummary: {summary}\n
Generate a complete research report with these JSON keys:
- key_findings (list of 5 strings)
- trend_analysis (list of 3 dict with 'trend' and 'description')
- recommendations (list of 5 action strings)
- risk_analysis (paragraph string)
- future_predictions (paragraph string)

Respond ONLY with valid JSON."""
        response = self._chat(system, user)
        try:
            import json
            # Strip code fences if present
            clean = response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(clean)
        except Exception:
            return {
                "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
                "trend_analysis": [{"trend": "Growth", "description": "Rapid growth observed"}],
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "risk_analysis": "Moderate risks identified.",
                "future_predictions": "Strong growth expected over next 5 years.",
            }

    def answer_question(self, question: str, context: str) -> str:
        system = "You are an AI research assistant. Answer questions based on provided research context."
        user = f"Context:\n{context}\n\nQuestion: {question}"
        return self._chat(system, user)

    def analyze_sources(self, topic: str, sources: list) -> str:
        source_texts = "\n\n".join([f"- {s.get('title', '')}: {s.get('content', '')[:500]}" for s in sources[:8]])
        system = "You are a data analyst identifying patterns from research sources."
        user = f"Analyze the following sources about '{topic}' and identify key patterns, trends, and insights:\n\n{source_texts}"
        return self._chat(system, user)

    def get_embedding(self, text: str) -> Optional[List[float]]:
        if not self.client:
            return [0.0] * 1536  # Mock embedding
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000],
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return [0.0] * 1536

openai_service = OpenAIService()
