import os
import json
from typing import Dict, List, Any, Optional
from models import ToolCall, AccessLevel

class MCPConnector:
    """Base class for MCP (Model Context Protocol) connectors"""
    
    def __init__(self, name: str):
        self.name = name
    
    def execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        raise NotImplementedError

class GitHubMCPConnector(MCPConnector):
    """MCP Connector for GitHub operations"""
    
    def __init__(self):
        super().__init__("github")
        # In a real implementation, this would connect to GitHub API
        self.mock_repos = {
            "user/web-app": {
                "files": ["src/auth.py", "src/api.py", "README.md"],
                "branches": ["main", "develop"],
                "issues": [{"id": 1, "title": "Authentication bug"}]
            },
            "user/infrastructure": {
                "files": ["scripts/deploy.sh", "configs/server.yml"],
                "branches": ["main"],
                "issues": []
            }
        }
    
    def execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute GitHub operations"""
        action = tool_call.action.lower()
        resource_path = tool_call.resource_path
        
        if action == "read":
            return self._read_repository(resource_path)
        elif action == "write" or action == "create":
            return self._write_repository(resource_path, tool_call.parameters)
        elif action == "list":
            return self._list_repositories()
        else:
            return {"error": f"Unsupported action: {action}"}
    
    def _read_repository(self, repo_path: str) -> Dict[str, Any]:
        """Mock reading from a repository"""
        if repo_path in self.mock_repos:
            return {
                "success": True,
                "data": self.mock_repos[repo_path],
                "message": f"Successfully read repository: {repo_path}"
            }
        else:
            return {
                "success": False,
                "error": f"Repository not found: {repo_path}"
            }
    
    def _write_repository(self, repo_path: str, parameters: Dict) -> Dict[str, Any]:
        """Mock writing to a repository"""
        # In real implementation, this would use GitHub API
        return {
            "success": True,
            "data": {"commit_id": "abc123", "message": "Changes committed"},
            "message": f"Successfully wrote to repository: {repo_path}"
        }
    
    def _list_repositories(self) -> Dict[str, Any]:
        """Mock listing repositories"""
        return {
            "success": True,
            "data": {"repositories": list(self.mock_repos.keys())},
            "message": "Successfully listed repositories"
        }

class FileSystemMCPConnector(MCPConnector):
    """MCP Connector for file system operations"""
    
    def __init__(self, base_path: str = "/tmp/mock_filesystem"):
        super().__init__("filesystem")
        self.base_path = base_path
        self._setup_mock_filesystem()
    
    def _setup_mock_filesystem(self):
        """Create mock file system structure"""
        os.makedirs(self.base_path, exist_ok=True)
        
        # Create persona-specific directories with sample files
        directories = {
            "engineering": [
                "design_docs/auth_system.md",
                "code_reviews/pr_123.md",
                "deployment_guides/production.md"
            ],
            "it": [
                "incident_reports/network_outage.md",
                "maintenance_scripts/server_update.sh",
                "troubleshooting_guides/connectivity.md"
            ],
            "sales": [
                "proposals/client_abc.docx",
                "collateral/product_brochure.pdf",
                "leads/healthcare_prospects.xlsx"
            ]
        }
        
        for persona, files in directories.items():
            persona_path = os.path.join(self.base_path, persona)
            os.makedirs(persona_path, exist_ok=True)
            
            for file_path in files:
                full_path = os.path.join(persona_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Create sample content based on file type
                content = self._generate_sample_content(file_path, persona)
                with open(full_path, 'w') as f:
                    f.write(content)
    
    def _generate_sample_content(self, file_path: str, persona: str) -> str:
        """Generate sample content for mock files"""
        if file_path.endswith('.md'):
            return f"# {os.path.basename(file_path)}\n\nSample content for {persona} team.\n"
        elif file_path.endswith('.sh'):
            return "#!/bin/bash\n# Sample maintenance script\necho 'Running maintenance...'\n"
        else:
            return f"Sample {persona} file content"
    
    def execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute file system operations"""
        action = tool_call.action.lower()
        resource_path = tool_call.resource_path
        
        # Convert resource path to actual file system path
        if resource_path.startswith('/'):
            resource_path = resource_path[1:]  # Remove leading slash
        
        full_path = os.path.join(self.base_path, resource_path)
        
        if action == "read":
            return self._read_file(full_path)
        elif action == "write" or action == "create":
            return self._write_file(full_path, tool_call.parameters)
        elif action == "list":
            return self._list_directory(full_path)
        elif action == "delete":
            return self._delete_file(full_path)
        else:
            return {"error": f"Unsupported action: {action}"}
    
    def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the file system"""
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                return {
                    "success": True,
                    "data": {"content": content, "path": file_path},
                    "message": f"Successfully read file: {file_path}"
                }
            else:
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }
    
    def _write_file(self, file_path: str, parameters: Dict) -> Dict[str, Any]:
        """Write to a file in the file system"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            content = parameters.get('content', 'Default content')
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                "success": True,
                "data": {"path": file_path, "size": len(content)},
                "message": f"Successfully wrote to file: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}"
            }
    
    def _list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List contents of a directory"""
        try:
            if os.path.isdir(dir_path):
                contents = os.listdir(dir_path)
                return {
                    "success": True,
                    "data": {"contents": contents, "path": dir_path},
                    "message": f"Successfully listed directory: {dir_path}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Directory not found: {dir_path}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing directory: {str(e)}"
            }
    
    def _delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file from the file system"""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return {
                    "success": True,
                    "data": {"path": file_path},
                    "message": f"Successfully deleted file: {file_path}"
                }
            else:
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error deleting file: {str(e)}"
            }

class MCPManager:
    """Manager for all MCP connectors"""
    
    def __init__(self):
        self.connectors = {
            "github": GitHubMCPConnector(),
            "filesystem": FileSystemMCPConnector()
        }
    
    def execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Route tool call to appropriate connector"""
        connector = self.connectors.get(tool_call.resource_type)
        if not connector:
            return {
                "success": False,
                "error": f"No connector available for resource type: {tool_call.resource_type}"
            }
        
        return connector.execute_tool_call(tool_call)
