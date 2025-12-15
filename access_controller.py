from typing import List
import fnmatch
from models import Permission, AccessLevel, ToolCall, AccessRequest, AccessResponse
from data import USERS, PERSONA_PERMISSIONS
from task_mapper import TaskMapper

class AccessController:
    def __init__(self):
        self.users = {user.user_id: user for user in USERS}
        self.task_mapper = TaskMapper()
        self.persona_permissions = PERSONA_PERMISSIONS
    
    def evaluate_access_request(self, request: AccessRequest) -> AccessResponse:
        """
        Evaluate an access request based on user persona and mapped tasks
        
        Args:
            request: AccessRequest containing user_id, prompt, and requested tool calls
            
        Returns:
            AccessResponse with access decision and details
        """
        user = self.users.get(request.user_id)
        if not user:
            return AccessResponse(
                allowed=False,
                mapped_tasks=[],
                denied_calls=request.requested_tool_calls,
                reason="User not found"
            )
        
        # Map prompt to tasks
        mapped_task_results = self.task_mapper.map_prompt_to_tasks(request.prompt)
        mapped_task_ids = [task_id for task_id, _ in mapped_task_results]
        
        if not mapped_task_ids:
            return AccessResponse(
                allowed=False,
                mapped_tasks=[],
                denied_calls=request.requested_tool_calls,
                reason="No tasks could be mapped from the prompt"
            )
        
        # Get user permissions based on persona
        user_permissions = self.persona_permissions.get(user.persona, [])
        
        # Evaluate each tool call
        denied_calls = []
        allowed_calls = []
        
        for tool_call in request.requested_tool_calls:
            if self._is_tool_call_allowed(tool_call, user_permissions):
                allowed_calls.append(tool_call)
            else:
                denied_calls.append(tool_call)
        
        # Determine overall access
        all_allowed = len(denied_calls) == 0
        
        reason = ""
        if not all_allowed:
            reason = f"Access denied for {len(denied_calls)} tool calls due to insufficient permissions"
        elif all_allowed and len(request.requested_tool_calls) > 0:
            reason = "All requested operations are allowed"
        else:
            reason = "No tool calls provided"
        
        return AccessResponse(
            allowed=all_allowed,
            mapped_tasks=mapped_task_ids,
            denied_calls=denied_calls,
            reason=reason
        )
    
    def _is_tool_call_allowed(self, tool_call: ToolCall, user_permissions: List[Permission]) -> bool:
        """
        Check if a specific tool call is allowed based on user permissions
        
        Args:
            tool_call: The tool call to evaluate
            user_permissions: List of permissions for the user
            
        Returns:
            True if allowed, False otherwise
        """
        required_access = self._get_required_access_level(tool_call.action)
        
        for permission in user_permissions:
            if (permission.resource_type == tool_call.resource_type and
                self._path_matches(tool_call.resource_path, permission.resource_path) and
                self._access_level_sufficient(permission.access_level, required_access)):
                return True
        
        return False
    
    def _get_required_access_level(self, action: str) -> AccessLevel:
        """
        Determine the required access level based on the action
        
        Args:
            action: The action being performed (read, write, create, delete, etc.)
            
        Returns:
            Required AccessLevel
        """
        write_actions = ['write', 'create', 'update', 'delete', 'modify', 'push', 'commit']
        
        if action.lower() in write_actions:
            return AccessLevel.WRITE
        else:
            return AccessLevel.READ
    
    def _path_matches(self, requested_path: str, permission_path: str) -> bool:
        """
        Check if a requested path matches a permission path pattern
        
        Args:
            requested_path: The path being requested
            permission_path: The permission path pattern (may contain wildcards)
            
        Returns:
            True if the path matches, False otherwise
        """
        return fnmatch.fnmatch(requested_path, permission_path)
    
    def _access_level_sufficient(self, granted_level: AccessLevel, required_level: AccessLevel) -> bool:
        """
        Check if the granted access level is sufficient for the required level
        
        Args:
            granted_level: The access level granted to the user
            required_level: The access level required for the operation
            
        Returns:
            True if sufficient, False otherwise
        """
        level_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2
        }
        
        return level_hierarchy[granted_level] >= level_hierarchy[required_level]
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        return self.persona_permissions.get(user.persona, [])
    
    def get_allowed_tasks_for_user(self, user_id: str) -> List[str]:
        """Get all task IDs that a user is allowed to perform"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        return [task.task_id for task in self.task_mapper.get_tasks_by_persona(user.persona)]
