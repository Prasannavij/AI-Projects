import os
import asyncio
import logging
from playwright.async_api import async_playwright

from agent.llm import MockLLMProvider, OllamaProvider
from agent.agent import SimpleAgent
from harness.harness import AgentHarness
from tools.browser import BrowserTools
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

async def main():
    print("\n=== AGENT HARNESS DEMONSTRATION ===\n")
    async with async_playwright() as p:
        
        # Use a local, isolated profile just for the agent instead of your personal Chrome profile.
        # This completely resolves the hanging/crashing issues!
        user_data_dir = os.path.join(os.getcwd(), "agent_chrome_profile")
        
        # Must launch headed
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False
        )
        
        # Grab the existing primary tab instead of opening a new one
        page = context.pages[0]

        # Initialize tools
        browser_tools = BrowserTools(page)
        browser_tools.register_tools()

        # Initialize LLM and Agent
        llm = OllamaProvider(model_name="qwen2.5:3b")
        agent = SimpleAgent(llm)

        # Initialize Harness
        harness = AgentHarness(agent)
        
        # A clean, highly reliable task perfect for proving the Harness and LLM work end-to-end
        goal = (
            "Open https://en.wikipedia.org/wiki/Software_agent. "
            "Use the get_page_text tool to read the page. "
            "Once you have read the text, use the finish tool. For the finish tool 'reason' argument, write a short 1-sentence summary of what a Software Agent is based on the text."
        )
        
        await harness.run(goal)
        
        await context.close()
        
if __name__ == "__main__":
    asyncio.run(main())
