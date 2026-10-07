def evaluate_success(goal: str, state) -> dict:
    # A simple evaluator, real world would use an LLM to evaluate if the goal is met 
    # based on state history and current observations.
    
    if state.last_action and state.last_action.get("action") == "finish":
        return {"complete": True, "reason": state.last_action.get("arguments", {}).get("reason", "Agent finished task")}
        
    return {"complete": False, "reason": "Task not explicitly finished"}
