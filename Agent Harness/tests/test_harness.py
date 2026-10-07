import pytest
from harness.harness import AgentHarness
from harness.state import AgentState
from agent.agent import SimpleAgent
from tools.registry import ToolRegistry

class MockAgent:
    def __init__(self, actions):
        self.actions = actions
        self.idx = 0
    async def decide(self, state):
        if self.idx < len(self.actions):
            action = self.actions[self.idx]
            self.idx += 1
            return action
        return {"action": "finish"}

@pytest.mark.asyncio
async def test_max_steps():
    async def dummy(): pass
    ToolRegistry.register("dummy", dummy, "Dummy tool")
    
    # 12 steps -> Should hit MAX_STEPS = 10
    agent = MockAgent([{"action": "dummy", "arguments": {}} for _ in range(12)])
    harness = AgentHarness(agent)
    
    async def mock_execute(*args): pass
    harness._execute_action = mock_execute
    
    state = await harness.run("test max steps")
    assert state.status == "terminated"
    assert state.current_step == 10

@pytest.mark.asyncio
async def test_policy_violation():
    async def mock_open_page(url): pass
    ToolRegistry.register("open_page", mock_open_page, "open page mock", schema={"url": "string"})
    
    agent = MockAgent([
        {"action": "open_page", "arguments": {"url": "https://blocked.com"}, "reason": ""}
    ])
    harness = AgentHarness(agent)
    state = await harness.run("test policy")
    
    # Should skip executing it, let's verify history
    assert state.current_step == 1
    
    # Check if any observation says policy violation
    policy_obs = next((h["data"] for h in state.history if h.get("type") == "observation" and h["data"].get("error")), None)
    assert policy_obs is not None
    assert policy_obs.get("error", {}).get("type") == "policy_violation"

@pytest.mark.asyncio
async def test_risky_action(monkeypatch):
    # setup a mock tool first
    from tools.registry import ToolRegistry
    async def mock_tool(): pass
    ToolRegistry.register("mock_risk", mock_tool, "Risk", risk_level="high", requires_approval=True)

    agent = MockAgent([
        {"action": "mock_risk", "arguments": {}}
    ])
    harness = AgentHarness(agent)
    
    state = await harness.run("test risk")
    
    risk_obs = next((h["data"] for h in state.history if h.get("type") == "observation" and h["data"].get("error")), None)
    assert risk_obs is not None
    assert risk_obs.get("error", {}).get("type") == "approval_required"

@pytest.mark.asyncio
async def test_retry_logic():
    # A mocked agent that keeps providing a valid tool that fails inside execution
    from tools.registry import ToolRegistry
    
    async def fail_tool():
        raise Exception("element not found")
        
    ToolRegistry.register("fail_tool", fail_tool, "Fail")
    
    agent = MockAgent([
        {"action": "fail_tool", "arguments": {}}
    ])
    harness = AgentHarness(agent)
    harness.state = AgentState(goal="retry")

    # Call directly
    await harness._execute_action("fail_tool", {}, ToolRegistry.get_tool("fail_tool"))
    
    assert harness.state.retry_count == 1
    
    # Retry again
    await harness._execute_action("fail_tool", {}, ToolRegistry.get_tool("fail_tool"))
    assert harness.state.retry_count == 2
    
    # Retry again -> Stop
    await harness._execute_action("fail_tool", {}, ToolRegistry.get_tool("fail_tool"))
    assert harness.state.status == "failed"
