from tools.registry import ToolRegistry

def validate_action(action_payload: dict) -> tuple[bool, str]:
    if not isinstance(action_payload, dict):
         return False, "Action payload is not a dictionary"
    
    action_name = action_payload.get("action")
    if not action_name:
         return False, "Missing 'action' key"
         
    if action_name == "finish":
        return True, ""
         
    tool = ToolRegistry.get_tool(action_name)
    if not tool:
         return False, f"Unknown tool: {action_name}"

    arguments = action_payload.get("arguments", {})
    if not isinstance(arguments, dict):
        return False, "'arguments' must be a dictionary"
        
    # Check schema lightly
    expected_schema = tool.get("schema", {})
    for key in expected_schema:
        if key not in arguments:
             return False, f"Missing required parameter '{key}' for tool {action_name}"
             
    return True, ""
