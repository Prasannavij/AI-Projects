import logging
from typing import Optional
from .state import AgentState
from .policies import check_action_policy
from .validator import validate_action
from .retry import RetryManager
from .evaluator import evaluate_success
from tools.registry import ToolRegistry
from agent.agent import SimpleAgent

logger = logging.getLogger(__name__)

class AgentHarness:
    def __init__(self, agent: SimpleAgent):
        self.agent = agent
        self.state: Optional[AgentState] = None
        self.retry_manager = RetryManager()

    async def run(self, goal: str):
        logger.info(f"Starting AgentHarness with goal: {goal}")
        self.state = AgentState(goal=goal)
        
        while self.state.status == "running":
            # 1. Check max steps
            if self.state.current_step >= self.state.max_steps:
                 self.state.status = "terminated"
                 logger.warning("Terminated: reason=max_steps_exceeded")
                 break
                 
            logger.info(f"\n--- STEP {self.state.current_step + 1} ---")
            
            # 2. Ask Agent for Action
            logger.info("Asking agent for next action...")
            action_request = await self.agent.decide(self.state)
            self.state.last_action = action_request
            self.state.history.append({"type": "agent_action", "data": action_request})
            logger.info(f"Agent Action Request: {action_request}")

            # 3. Validate Action Schema
            is_valid, validation_msg = validate_action(action_request)
            if not is_valid:
                 logger.error(f"Validation failed: {validation_msg}")
                 self._handle_failure({"type": "validation_error", "message": validation_msg})
                 continue
                 
            action_name = action_request.get("action")
            
            if action_name == "finish":
                 logger.info("Agent decided to finish.")
                 self.state.history.append({"type": "observation", "data": {"message": "Agent finished task"}})
                 break

            arguments = action_request.get("arguments", {})
            tool_meta = ToolRegistry.get_tool(action_name)

            # 4. Check Policy
            policy_result = check_action_policy(action_name, arguments, tool_meta)
            if not policy_result.get("allowed"):
                logger.warning(f"Policy rejection: {policy_result}")
                self._handle_failure({
                    "type": "policy_violation" if policy_result["reason"] == "policy_violation" else "approval_required",
                    "message": policy_result["message"]
                })
                if policy_result["reason"] == "requires_approval":
                    logger.info(">>> HUMAN APPROVAL REQUIRED <<<")
                    # In a real app we would pause execution here. In a console app we can ask via input.
                    # As an automated tests run we skip input if standard streams aren't available, but we'll simulate denial.
                    logger.info("Action Denied - mock human input.")
                    self.state.current_step += 1
                else:
                    self.state.current_step += 1
                continue
            
            # 5. Execute Action
            await self._execute_action(action_name, arguments, tool_meta)
            
            # 6. Evaluate Result
            eval_result = evaluate_success(self.state.goal, self.state)
            if eval_result["complete"]:
                self.state.status = "success"
                logger.info(f"Task completed successfully: {eval_result['reason']}")
                break
                
            self.state.current_step += 1

        logger.info(f"AgentHarness finished with status: {self.state.status}")
        return self.state

    async def _execute_action(self, action_name: str, arguments: dict, tool_meta: dict):
        logger.info(f"Executing tool: {action_name} with {arguments}")
        try:
            func = tool_meta["func"]
            # Call tool with arguments as kwargs
            result = await func(**arguments)
            
            # Collect observation
            obs = {
                 "success": True,
                 "tool": action_name,
                 "data": result,
                 "error": None
            }
            logger.info(f"Observation: {obs}")
            self.state.last_observation = obs
            self.state.history.append({"type": "observation", "data": obs})
            self.state.retry_count = 0 # reset retries on success

            # update state URL/Title dynamically
            if "current_url" in result: self.state.current_url = result["current_url"]
            if "title" in result: self.state.current_title = result["title"]
            
        except Exception as e:
            logger.error(f"Tool execution Exception: {e}")
            self._handle_failure({"type": "tool_exception", "message": str(e)})


    def _handle_failure(self, error: dict):
        error_class = self.retry_manager.classify_error(Exception(f"[{error.get('type')}] {error.get('message')}"))
        logger.error(f"Failure classified as: {error_class}")
        
        obs = {
            "success": False,
            "tool": self.state.last_action.get("action") if self.state.last_action else "unknown",
            "data": None,
            "error": error
        }
        self.state.last_observation = obs
        self.state.history.append({"type": "observation", "data": obs})
        
        if self.retry_manager.can_retry(error_class, self.state.retry_count):
             self.state.retry_count += 1
             logger.info(f"Retrying... {self.state.retry_count}/{self.state.max_retries}")
        else:
             if error_class not in ["POLICY_VIOLATION", "USER_ACTION_REQUIRED"]:
                  logger.error("Max retries reached or non-recoverable error.")
                  self.state.status = "failed"
