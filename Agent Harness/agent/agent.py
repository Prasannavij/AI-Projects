import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimpleAgent:
    def __init__(self, llm_provider):
        self.llm = llm_provider

    async def decide(self, state) -> Dict[str, Any]:
        """Query LLM to decide on the next action based on state details."""
        prompt = self._build_prompt(state)
        response_text = await self.llm.generate(prompt)
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                json_str = response_text[start:end+1]
                return json.loads(json_str)
            else:
                return {"action": "unknown", "arguments": {}, "reason": "Failed to parse json"}
        except json.JSONDecodeError:
            return {"action": "parse_error", "arguments": {"raw": response_text}}

    def _build_prompt(self, state) -> str:
        prompt = f"""
You are a browser assistant agent.
Your Goal: {state.goal}
Current URL: {state.current_url}
Current Title: {state.current_title}

Action History:
"""
        for h in state.history[-5:]:
            prompt += f"- {json.dumps(h)}\n"

        prompt += """
Respond with a JSON object, exactly matching this structure, no other text:
{
    "action": "tool_name",
    "arguments": {"key": "value"},
    "reason": "Why you chose this action"
}
Available tools:
- open_page (url)
- get_page_text ()
- get_page_title ()
- click (selector)
- click_by_text (text)
- type_text (selector, text)
- go_back ()
- take_screenshot ()
- submit_form (selector)
- finish (reason)
"""
        return prompt
