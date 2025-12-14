from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from typing import List, Dict
from models import AccessRequest, AccessResponse, User, Task
from access_controller import AccessController
from mcp_connectors import MCPManager
from data import USERS, TASKS

app = FastAPI(title="Task-Based Access Pattern Model", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Initialize components
access_controller = AccessController()
mcp_manager = MCPManager()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Task-Based Access Pattern Model</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            .user-select { margin: 10px 0; }
            .prompt-input { width: 100%; height: 100px; margin: 10px 0; }
            .tool-call { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 4px; }
            .result { margin: 10px 0; padding: 15px; border-radius: 4px; }
            .allowed { background: #d4edda; border: 1px solid #c3e6cb; }
            .denied { background: #f8d7da; border: 1px solid #f5c6cb; }
            button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .add-btn { background: #28a745; }
            .remove-btn { background: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Task-Based Access Pattern Model</h1>
            
            <div class="section">
                <h2>User Selection</h2>
                <select id="userSelect" class="user-select">
                    <option value="">Select a user...</option>
                </select>
                <div id="userInfo"></div>
            </div>
            
            <div class="section">
                <h2>Prompt Input</h2>
                <textarea id="promptInput" class="prompt-input" placeholder="Enter your prompt here..."></textarea>
            </div>
            
            <div class="section">
                <h2>Tool Calls</h2>
                <div id="toolCalls">
                    <div class="tool-call">
                        <label>Resource Type:</label>
                        <select class="resource-type">
                            <option value="github">GitHub</option>
                            <option value="filesystem">File System</option>
                        </select>
                        <label>Resource Path:</label>
                        <input type="text" class="resource-path" placeholder="e.g., user/repo or /engineering/docs">
                        <label>Action:</label>
                        <select class="action">
                            <option value="read">Read</option>
                            <option value="write">Write</option>
                            <option value="create">Create</option>
                            <option value="delete">Delete</option>
                            <option value="list">List</option>
                        </select>
                        <button class="remove-btn" onclick="removeToolCall(this)">Remove</button>
                    </div>
                </div>
                <button class="add-btn" onclick="addToolCall()">Add Tool Call</button>
            </div>
            
            <div class="section">
                <button onclick="evaluateAccess()">Evaluate Access</button>
                <button onclick="executeToolCalls()">Execute Tool Calls</button>
            </div>
            
            <div class="section">
                <h2>Results</h2>
                <div id="results"></div>
            </div>
        </div>

        <script>
            // Load users on page load
            window.onload = function() {
                loadUsers();
            };

            async function loadUsers() {
                try {
                    const response = await fetch('/users');
                    const users = await response.json();
                    const select = document.getElementById('userSelect');
                    
                    users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.user_id;
                        option.textContent = `${user.name} (${user.team})`;
                        select.appendChild(option);
                    });
                    
                    select.addEventListener('change', function() {
                        if (this.value) {
                            showUserInfo(users.find(u => u.user_id === this.value));
                        } else {
                            document.getElementById('userInfo').innerHTML = '';
                        }
                    });
                } catch (error) {
                    console.error('Error loading users:', error);
                }
            }

            function showUserInfo(user) {
                document.getElementById('userInfo').innerHTML = `
                    <p><strong>Name:</strong> ${user.name}</p>
                    <p><strong>Team:</strong> ${user.team}</p>
                    <p><strong>Persona:</strong> ${user.persona}</p>
                    <p><strong>Location:</strong> ${user.location}</p>
                `;
            }

            function addToolCall() {
                const toolCallsDiv = document.getElementById('toolCalls');
                const newToolCall = document.createElement('div');
                newToolCall.className = 'tool-call';
                newToolCall.innerHTML = `
                    <label>Resource Type:</label>
                    <select class="resource-type">
                        <option value="github">GitHub</option>
                        <option value="filesystem">File System</option>
                    </select>
                    <label>Resource Path:</label>
                    <input type="text" class="resource-path" placeholder="e.g., user/repo or /engineering/docs">
                    <label>Action:</label>
                    <select class="action">
                        <option value="read">Read</option>
                        <option value="write">Write</option>
                        <option value="create">Create</option>
                        <option value="delete">Delete</option>
                        <option value="list">List</option>
                    </select>
                    <button class="remove-btn" onclick="removeToolCall(this)">Remove</button>
                `;
                toolCallsDiv.insertBefore(newToolCall, toolCallsDiv.lastElementChild);
            }

            function removeToolCall(button) {
                button.parentElement.remove();
            }

            function getToolCalls() {
                const toolCallElements = document.querySelectorAll('.tool-call');
                const toolCalls = [];
                
                toolCallElements.forEach(element => {
                    const resourceType = element.querySelector('.resource-type').value;
                    const resourcePath = element.querySelector('.resource-path').value;
                    const action = element.querySelector('.action').value;
                    
                    if (resourcePath) {
                        toolCalls.push({
                            tool_name: resourceType,
                            resource_type: resourceType,
                            resource_path: resourcePath,
                            action: action,
                            parameters: {}
                        });
                    }
                });
                
                return toolCalls;
            }

            async function evaluateAccess() {
                const userId = document.getElementById('userSelect').value;
                const prompt = document.getElementById('promptInput').value;
                const toolCalls = getToolCalls();
                
                if (!userId || !prompt) {
                    alert('Please select a user and enter a prompt');
                    return;
                }
                
                try {
                    const response = await fetch('/evaluate-access', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            user_id: userId,
                            prompt: prompt,
                            requested_tool_calls: toolCalls
                        })
                    });
                    
                    const result = await response.json();
                    displayResult(result, 'Access Evaluation');
                } catch (error) {
                    console.error('Error evaluating access:', error);
                    alert('Error evaluating access');
                }
            }

            async function executeToolCalls() {
                const userId = document.getElementById('userSelect').value;
                const prompt = document.getElementById('promptInput').value;
                const toolCalls = getToolCalls();
                
                if (!userId || !prompt) {
                    alert('Please select a user and enter a prompt');
                    return;
                }
                
                try {
                    const response = await fetch('/execute', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            user_id: userId,
                            prompt: prompt,
                            requested_tool_calls: toolCalls
                        })
                    });
                    
                    const result = await response.json();
                    displayResult(result, 'Execution Result');
                } catch (error) {
                    console.error('Error executing tool calls:', error);
                    alert('Error executing tool calls');
                }
            }

            function displayResult(result, title) {
                const resultsDiv = document.getElementById('results');
                const resultDiv = document.createElement('div');
                resultDiv.className = `result ${result.allowed ? 'allowed' : 'denied'}`;
                
                let html = `<h3>${title}</h3>`;
                html += `<p><strong>Allowed:</strong> ${result.allowed}</p>`;
                html += `<p><strong>Reason:</strong> ${result.reason}</p>`;
                html += `<p><strong>Mapped Tasks:</strong> ${result.mapped_tasks.join(', ')}</p>`;
                
                if (result.denied_calls && result.denied_calls.length > 0) {
                    html += `<p><strong>Denied Calls:</strong></p><ul>`;
                    result.denied_calls.forEach(call => {
                        html += `<li>${call.action} on ${call.resource_type}:${call.resource_path}</li>`;
                    });
                    html += `</ul>`;
                }
                
                if (result.execution_results) {
                    html += `<p><strong>Execution Results:</strong></p>`;
                    result.execution_results.forEach((execResult, index) => {
                        html += `<div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px;">`;
                        html += `<strong>Tool Call ${index + 1}:</strong><br>`;
                        html += `<pre style="background: #f8f9fa; padding: 5px; border-radius: 3px; font-size: 12px;">${JSON.stringify(execResult, null, 2)}</pre>`;
                        html += `</div>`;
                    });
                }
                
                resultDiv.innerHTML = html;
                resultsDiv.appendChild(resultDiv);
            }
        </script>
    </body>
    </html>
    """

@app.get("/users")
async def get_users() -> List[User]:
    """Get all users"""
    return USERS

@app.get("/tasks")
async def get_tasks() -> List[Task]:
    """Get all tasks"""
    return TASKS

@app.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str):
    """Get permissions for a specific user"""
    permissions = access_controller.get_user_permissions(user_id)
    return {"user_id": user_id, "permissions": permissions}

@app.get("/users/{user_id}/tasks")
async def get_user_tasks(user_id: str):
    """Get allowed tasks for a specific user"""
    tasks = access_controller.get_allowed_tasks_for_user(user_id)
    return {"user_id": user_id, "allowed_tasks": tasks}

@app.post("/map-tasks")
async def map_tasks(request: Dict[str, str]):
    """Map a prompt to tasks"""
    prompt = request.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    mapped_tasks = access_controller.task_mapper.map_prompt_to_tasks(prompt)
    keywords = access_controller.task_mapper.analyze_prompt_keywords(prompt)
    
    return {
        "prompt": prompt,
        "mapped_tasks": mapped_tasks,
        "keywords": keywords
    }

@app.post("/evaluate-access")
async def evaluate_access(request: AccessRequest) -> AccessResponse:
    """Evaluate an access request"""
    try:
        return access_controller.evaluate_access_request(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating access: {str(e)}")

@app.post("/execute")
async def execute_tool_calls(request: AccessRequest):
    """Execute tool calls after access evaluation"""
    try:
        # First evaluate access
        access_response = access_controller.evaluate_access_request(request)
        
        if not access_response.allowed:
            return {
                "allowed": False,
                "mapped_tasks": access_response.mapped_tasks,
                "denied_calls": access_response.denied_calls,
                "reason": access_response.reason,
                "execution_results": []
            }
        
        # Execute allowed tool calls
        execution_results = []
        for tool_call in request.requested_tool_calls:
            if tool_call not in access_response.denied_calls:
                result = mcp_manager.execute_tool_call(tool_call)
                execution_results.append({
                    "tool_call": tool_call.dict(),
                    "result": result
                })
        
        return {
            "allowed": True,
            "mapped_tasks": access_response.mapped_tasks,
            "denied_calls": [],
            "reason": "All tool calls executed successfully",
            "execution_results": execution_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool calls: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
