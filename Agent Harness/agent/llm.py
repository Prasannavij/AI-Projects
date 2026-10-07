import asyncio
import logging
import ollama

logger = logging.getLogger(__name__)

class OllamaProvider:
    """Connects out to your local Ollama instance."""
    def __init__(self, model_name: str = "qwen2.5:3b"):
        self.model_name = model_name
        self.client = ollama.AsyncClient()

    async def generate(self, prompt: str, enforce_json: bool = True) -> str:
        logger.info(f"Thinking using Ollama ({self.model_name})...")
        try:
            kwargs = {
                "model": self.model_name,
                "prompt": prompt,
                "options": {"temperature": 0.0}
            }
            if enforce_json:
                kwargs["format"] = "json"
                
            response = await self.client.generate(**kwargs)
            return response['response']
        except Exception as e:
            logger.error(f"Failed to communicate with Ollama: {e}")
            return '{"action": "finish", "arguments": {"reason": "Ollama connection failure"}, "reason": "abort"}'

class MockLLMProvider:
    """A mock LLM Provider to simulate interactions without API keys for testing."""
    def __init__(self):
        self.steps = 0
        
    async def generate(self, prompt: str) -> str:
        logging.getLogger(__name__).debug(f"MockLLM received prompt length: {len(prompt)}")
        await asyncio.sleep(0.5)
        
        if self.steps == 0:
            self.steps += 1
            return '{"action": "open_page", "arguments": {"url": "https://example.com"}, "reason": "Initialize task"}'
        elif self.steps == 1:
            self.steps += 1
            return '{"action": "open_page", "arguments": {"url": "https://blocked-domain.com"}, "reason": "Try a bad site"}'
        elif self.steps == 2:
            self.steps += 1
            return '{"action": "click", "arguments": {"selector": "#missing-element"}, "reason": "Try a bad selector"}'
        elif self.steps == 3:
            self.steps += 1
            return '{"action": "get_page_text", "arguments": {}, "reason": "Get text"}'
        elif self.steps == 4:
            self.steps += 1
            return '{"action": "submit_form", "arguments": {"selector": "#submit"}, "reason": "Try a risky tool"}'
        elif self.steps == 5:
            self.steps += 1
            return '{"action": "finish", "arguments": {"reason": "Sequence complete"}, "reason": "Done"}'
        
        return '{"action": "finish", "arguments": {"reason": "End of mock"}, "reason": "Done"}'
