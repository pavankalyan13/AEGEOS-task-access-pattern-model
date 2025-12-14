from models import User, Task, Permission, PersonaType, TaskType, AccessLevel

# Sample Users
USERS = [
    User(
        user_id="eng01",
        name="Alex Chen",
        team="Engineering",
        persona=PersonaType.ENGINEERING,
        location="US"
    ),
    User(
        user_id="it01",
        name="Priya Nair",
        team="IT",
        persona=PersonaType.IT,
        location="Germany"
    ),
    User(
        user_id="sales01",
        name="Marco Diaz",
        team="Sales",
        persona=PersonaType.SALES,
        location="India"
    )
]

# Task Definitions with Required Permissions
TASKS = [
    Task(
        task_id="feat_dev_001",
        task_type=TaskType.FEATURE_DEVELOPMENT,
        description="Develop new product features, create/modify code repositories",
        required_permissions=[
            Permission(resource_type="github", resource_path="*", access_level=AccessLevel.WRITE),
            Permission(resource_type="filesystem", resource_path="/engineering/*", access_level=AccessLevel.WRITE)
        ],
        persona=PersonaType.ENGINEERING
    ),
    Task(
        task_id="prod_support_001",
        task_type=TaskType.PRODUCTION_SUPPORT,
        description="Debug production issues, analyze logs, hotfix deployment",
        required_permissions=[
            Permission(resource_type="github", resource_path="*", access_level=AccessLevel.WRITE),
            Permission(resource_type="filesystem", resource_path="/engineering/*", access_level=AccessLevel.READ)
        ],
        persona=PersonaType.ENGINEERING
    ),
    Task(
        task_id="incident_res_001",
        task_type=TaskType.INCIDENT_RESOLUTION,
        description="Resolve ITSM tickets, troubleshoot infrastructure issues",
        required_permissions=[
            Permission(resource_type="github", resource_path="*", access_level=AccessLevel.READ),
            Permission(resource_type="filesystem", resource_path="/it/*", access_level=AccessLevel.WRITE)
        ],
        persona=PersonaType.IT
    ),
    Task(
        task_id="infra_maint_001",
        task_type=TaskType.INFRASTRUCTURE_MAINTENANCE,
        description="Execute infrastructure scripts, system maintenance",
        required_permissions=[
            Permission(resource_type="filesystem", resource_path="/it/*", access_level=AccessLevel.WRITE),
            Permission(resource_type="github", resource_path="*/infrastructure", access_level=AccessLevel.READ)
        ],
        persona=PersonaType.IT
    ),
    Task(
        task_id="lead_gen_001",
        task_type=TaskType.LEAD_GENERATION,
        description="Drive outbound campaigns, prospect research",
        required_permissions=[
            Permission(resource_type="filesystem", resource_path="/sales/*", access_level=AccessLevel.WRITE)
        ],
        persona=PersonaType.SALES
    ),
    Task(
        task_id="proposal_dev_001",
        task_type=TaskType.PROPOSAL_DEVELOPMENT,
        description="Create proposals, manage sales collateral",
        required_permissions=[
            Permission(resource_type="filesystem", resource_path="/sales/*", access_level=AccessLevel.WRITE)
        ],
        persona=PersonaType.SALES
    )
]

# Sample Prompts for Training/Testing
SAMPLE_PROMPTS = [
    {
        "text": "I need to implement a new authentication feature for our web application",
        "expected_tasks": ["feat_dev_001"],
        "persona": PersonaType.ENGINEERING
    },
    {
        "text": "The production server is down, I need to check the logs and deploy a hotfix",
        "expected_tasks": ["prod_support_001"],
        "persona": PersonaType.ENGINEERING
    },
    {
        "text": "There's a network connectivity issue reported in ticket #1234, need to investigate",
        "expected_tasks": ["incident_res_001"],
        "persona": PersonaType.IT
    },
    {
        "text": "I need to update the server configurations and run the maintenance scripts",
        "expected_tasks": ["infra_maint_001"],
        "persona": PersonaType.IT
    },
    {
        "text": "Help me create a proposal for the new client meeting next week",
        "expected_tasks": ["proposal_dev_001"],
        "persona": PersonaType.SALES
    },
    {
        "text": "I want to research potential leads in the healthcare sector",
        "expected_tasks": ["lead_gen_001"],
        "persona": PersonaType.SALES
    },
    {
        "text": "Can you help me debug this API endpoint that's returning 500 errors?",
        "expected_tasks": ["prod_support_001"],
        "persona": PersonaType.ENGINEERING
    },
    {
        "text": "I need to add a new microservice to handle payment processing",
        "expected_tasks": ["feat_dev_001"],
        "persona": PersonaType.ENGINEERING
    }
]

# Persona Permissions Matrix
PERSONA_PERMISSIONS = {
    PersonaType.ENGINEERING: [
        Permission(resource_type="github", resource_path="*", access_level=AccessLevel.WRITE),
        Permission(resource_type="filesystem", resource_path="/engineering/*", access_level=AccessLevel.WRITE)
    ],
    PersonaType.IT: [
        Permission(resource_type="github", resource_path="*", access_level=AccessLevel.READ),
        Permission(resource_type="filesystem", resource_path="/it/*", access_level=AccessLevel.WRITE)
    ],
    PersonaType.SALES: [
        Permission(resource_type="filesystem", resource_path="/sales/*", access_level=AccessLevel.WRITE)
    ]
}
