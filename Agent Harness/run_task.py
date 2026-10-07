import sys
import os
import json
import asyncio
import logging
from playwright.async_api import async_playwright

from agent.llm import OllamaProvider
from agent.agent import SimpleAgent
from harness.harness import AgentHarness
from tools.browser import BrowserTools

async def execute_task(url: str):
    async with async_playwright() as p:
        user_data_dir = os.path.join(os.getcwd(), "agent_chrome_profile")
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=True # Running headlessly for a Background Web App!
        )
        page = context.pages[0]

        browser_tools = BrowserTools(page)
        browser_tools.register_tools()

        llm = OllamaProvider(model_name="qwen2.5:3b")
        agent = SimpleAgent(llm)
        harness = AgentHarness(agent)
        
        goal = (
            f"Open {url}. "
            "Next, use the get_page_text tool. "
            "Finally, you MUST use the finish tool to output the summary. You must output exactly this format: {\"action\": \"finish\", \"arguments\": {\"reason\": \"Write 1 sentence summarizing the website here\"}}"
        )
        
        state = await harness.run(goal)
        await context.close()
        
        # Post-Processing phase
        os.makedirs("outputs", exist_ok=True)
        
        # 1. Output details.json (the full action/observation log)
        details = {
            "target_url": url,
            "status": state.status,
            "steps_taken": state.current_step,
            "history": state.history
        }
        with open("outputs/details.json", "w", encoding="utf-8") as f:
            json.dump(details, f, indent=4)
            
        # 2. Output summary.txt
        summary_text = "Failed to extract summary."
        
        # Check if the agent successfully used the finish tool itself
        if state.last_action and state.last_action.get("action") == "finish":
             summary_text = state.last_action.get("arguments", {}).get("reason", summary_text)
        else:
             # Fallback: If the small model got trapped in an infinite loop, manually extract the webpage text 
             # from its observation history and force the LLM to summarize it directly, bypassing the Harness!
             for h in reversed(state.history):
                  if h.get("type") == "observation" and h.get("data") and "text" in h["data"].get("data", {}):
                       raw_text = h["data"]["data"]["text"]
                       logging.info("Harness fallback: Forcing direct LLM summarization...")
                       
                       prompt = f"Summarize the following website content in 2 clear sentences:\n\n{raw_text[:5000]}"
                       # Note we pass enforce_json=False because we want plain readable text!
                       summary_text = await llm.generate(prompt, enforce_json=False)
                       break
                
        with open("outputs/summary.txt", "w", encoding="utf-8") as f:
            f.write(f"submitted_url: {url}\n")
            f.write(f"page_summary: {summary_text}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        asyncio.run(execute_task(url))
