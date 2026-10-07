from playwright.async_api import Page
from .registry import ToolRegistry
import config

class BrowserTools:
    def __init__(self, page: Page):
        self.page = page

    async def open_page(self, url: str):
        await self.page.goto(url, timeout=config.ACTION_TIMEOUT)
        return {"current_url": self.page.url, "title": await self.page.title()}

    async def get_page_text(self):
        text = await self.page.evaluate("document.body.innerText")
        return {"text": text[:10000]} # Give the AI 10,000 characters so it can actually read past the header!

    async def get_page_title(self):
        return {"title": await self.page.title()}

    async def click(self, selector: str):
        await self.page.click(selector, timeout=config.ACTION_TIMEOUT)
        return {"clicked": selector}

    async def type_text(self, selector: str, text: str):
        await self.page.fill(selector, text, timeout=config.ACTION_TIMEOUT)
        return {"typed": text, "selector": selector}

    async def go_back(self):
        await self.page.go_back(timeout=config.ACTION_TIMEOUT)
        return {"current_url": self.page.url}

    async def take_screenshot(self):
        path = "logs/screenshot.png"
        import os
        os.makedirs("logs", exist_ok=True)
        await self.page.screenshot(path=path)
        return {"screenshot_path": path}

    async def click_by_text(self, text: str):
        # We MUST filter by only visible elements, otherwise GitHub's hidden mobile menus trap the AI!
        locator = self.page.locator(f"text=\"{text}\"").locator("visible=true").first
        await locator.click(timeout=config.ACTION_TIMEOUT)
        return {"clicked_text": text}

    def register_tools(self):
        ToolRegistry.register("open_page", self.open_page, "Navigate to a URL", schema={"url": "string"})
        ToolRegistry.register("get_page_text", self.get_page_text, "Get visible text")
        ToolRegistry.register("get_page_title", self.get_page_title, "Get page title")
        ToolRegistry.register("click", self.click, "Click on a CSS selector", schema={"selector": "string"})
        ToolRegistry.register("click_by_text", self.click_by_text, "Click on visible text (Much better for AI)", schema={"text": "string"})
        ToolRegistry.register("type_text", self.type_text, "Type text into a selector", schema={"selector": "string", "text": "string"})
        ToolRegistry.register("go_back", self.go_back, "Go back to previous page")
        ToolRegistry.register("take_screenshot", self.take_screenshot, "Take screenshot")
        
        # Risky mock tool for testing explicit policy rules
        async def submit_form(selector: str):
            # Normally: await self.page.click(selector)
            return {"submitted": selector, "status": "success"}
        ToolRegistry.register("submit_form", submit_form, "Submit form", risk_level="high", requires_approval=True, schema={"selector": "string"})
