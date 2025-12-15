#!/usr/bin/env python3
"""
Command Line Interface for Task-Based Access Pattern Model
"""

import argparse
import json
import sys
from typing import List
from models import AccessRequest, ToolCall
from access_controller import AccessController
from mcp_connectors import MCPManager
from data import USERS, TASKS

class CLI:
    def __init__(self):
        self.access_controller = AccessController()
        self.mcp_manager = MCPManager()
    
    def list_users(self):
        """List all users"""
        print("\n=== Users ===")
        for user in USERS:
            print(f"ID: {user.user_id}")
            print(f"Name: {user.name}")
            print(f"Team: {user.team}")
            print(f"Persona: {user.persona}")
            print(f"Location: {user.location}")
            print("-" * 40)
    
    def list_tasks(self):
        """List all tasks"""
        print("\n=== Tasks ===")
        for task in TASKS:
            print(f"ID: {task.task_id}")
            print(f"Type: {task.task_type}")
            print(f"Description: {task.description}")
            print(f"Persona: {task.persona}")
            print(f"Permissions: {len(task.required_permissions)} required")
            print("-" * 40)
    
    def show_user_permissions(self, user_id: str):
        """Show permissions for a specific user"""
        permissions = self.access_controller.get_user_permissions(user_id)
        user = next((u for u in USERS if u.user_id == user_id), None)
        
        if not user:
            print(f"User {user_id} not found")
            return
        
        print(f"\n=== Permissions for {user.name} ({user_id}) ===")
        print(f"Persona: {user.persona}")
        
        if not permissions:
            print("No permissions found")
            return
        
        for perm in permissions:
            print(f"Resource: {perm.resource_type}")
            print(f"Path: {perm.resource_path}")
            print(f"Access: {perm.access_level}")
            print("-" * 30)
    
    def map_prompt(self, prompt: str):
        """Map a prompt to tasks"""
        print(f"\n=== Mapping Prompt ===")
        print(f"Prompt: {prompt}")
        
        mapped_tasks = self.access_controller.task_mapper.map_prompt_to_tasks(prompt)
        keywords = self.access_controller.task_mapper.analyze_prompt_keywords(prompt)
        
        print(f"\n--- Mapped Tasks ---")
        if mapped_tasks:
            for task_id, confidence in mapped_tasks:
                task = self.access_controller.task_mapper.get_task_by_id(task_id)
                print(f"Task: {task_id} (confidence: {confidence:.3f})")
                print(f"Type: {task.task_type}")
                print(f"Description: {task.description}")
                print("-" * 30)
        else:
            print("No tasks mapped")
        
        print(f"\n--- Keywords Found ---")
        if keywords:
            for task_type, kw_list in keywords.items():
                print(f"{task_type}: {', '.join(kw_list)}")
        else:
            print("No keywords found")
    
    def evaluate_access(self, user_id: str, prompt: str, tool_calls_json: str):
        """Evaluate access for a user prompt and tool calls"""
        try:
            tool_calls_data = json.loads(tool_calls_json)
            tool_calls = [ToolCall(**tc) for tc in tool_calls_data]
        except json.JSONDecodeError as e:
            print(f"Error parsing tool calls JSON: {e}")
            return
        except Exception as e:
            print(f"Error creating tool calls: {e}")
            return
        
        request = AccessRequest(
            user_id=user_id,
            prompt=prompt,
            requested_tool_calls=tool_calls
        )
        
        response = self.access_controller.evaluate_access_request(request)
        
        print(f"\n=== Access Evaluation ===")
        print(f"User: {user_id}")
        print(f"Prompt: {prompt}")
        print(f"Allowed: {response.allowed}")
        print(f"Reason: {response.reason}")
        print(f"Mapped Tasks: {', '.join(response.mapped_tasks)}")
        
        if response.denied_calls:
            print(f"\n--- Denied Tool Calls ---")
            for call in response.denied_calls:
                print(f"Action: {call.action}")
                print(f"Resource: {call.resource_type}:{call.resource_path}")
                print("-" * 20)
    
    def execute_tool_calls(self, user_id: str, prompt: str, tool_calls_json: str):
        """Execute tool calls after access evaluation"""
        try:
            tool_calls_data = json.loads(tool_calls_json)
            tool_calls = [ToolCall(**tc) for tc in tool_calls_data]
        except json.JSONDecodeError as e:
            print(f"Error parsing tool calls JSON: {e}")
            return
        except Exception as e:
            print(f"Error creating tool calls: {e}")
            return
        
        request = AccessRequest(
            user_id=user_id,
            prompt=prompt,
            requested_tool_calls=tool_calls
        )
        
        # Evaluate access first
        access_response = self.access_controller.evaluate_access_request(request)
        
        print(f"\n=== Execution Results ===")
        print(f"User: {user_id}")
        print(f"Access Allowed: {access_response.allowed}")
        
        if not access_response.allowed:
            print(f"Reason: {access_response.reason}")
            return
        
        # Execute allowed tool calls
        print(f"\n--- Executing Tool Calls ---")
        for i, tool_call in enumerate(tool_calls):
            if tool_call not in access_response.denied_calls:
                print(f"\nExecuting tool call {i+1}:")
                print(f"Action: {tool_call.action}")
                print(f"Resource: {tool_call.resource_type}:{tool_call.resource_path}")
                
                result = self.mcp_manager.execute_tool_call(tool_call)
                print(f"Result: {json.dumps(result, indent=2)}")
            else:
                print(f"\nSkipping denied tool call {i+1}")

def main():
    parser = argparse.ArgumentParser(description="Task-Based Access Pattern Model CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List users command
    subparsers.add_parser("list-users", help="List all users")
    
    # List tasks command
    subparsers.add_parser("list-tasks", help="List all tasks")
    
    # Show user permissions command
    perm_parser = subparsers.add_parser("user-permissions", help="Show user permissions")
    perm_parser.add_argument("user_id", help="User ID")
    
    # Map prompt command
    map_parser = subparsers.add_parser("map-prompt", help="Map prompt to tasks")
    map_parser.add_argument("prompt", help="Prompt text")
    
    # Evaluate access command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate access request")
    eval_parser.add_argument("user_id", help="User ID")
    eval_parser.add_argument("prompt", help="Prompt text")
    eval_parser.add_argument("tool_calls", help="Tool calls JSON")
    
    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute tool calls")
    exec_parser.add_argument("user_id", help="User ID")
    exec_parser.add_argument("prompt", help="Prompt text")
    exec_parser.add_argument("tool_calls", help="Tool calls JSON")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLI()
    
    if args.command == "list-users":
        cli.list_users()
    elif args.command == "list-tasks":
        cli.list_tasks()
    elif args.command == "user-permissions":
        cli.show_user_permissions(args.user_id)
    elif args.command == "map-prompt":
        cli.map_prompt(args.prompt)
    elif args.command == "evaluate":
        cli.evaluate_access(args.user_id, args.prompt, args.tool_calls)
    elif args.command == "execute":
        cli.execute_tool_calls(args.user_id, args.prompt, args.tool_calls)

if __name__ == "__main__":
    main()
