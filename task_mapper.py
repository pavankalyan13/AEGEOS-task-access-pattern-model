import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from models import Task, TaskType, PersonaType
from data import TASKS, SAMPLE_PROMPTS

class TaskMapper:
    def __init__(self):
        self.tasks = {task.task_id: task for task in TASKS}
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.task_vectors = None
        self.task_descriptions = []
        self.task_ids = []
        self._train_model()
    
    def _train_model(self):
        """Train the task mapping model using task descriptions and sample prompts"""
        # Combine task descriptions with sample prompts for better training
        training_texts = []
        training_task_ids = []
        
        # Add task descriptions
        for task in TASKS:
            training_texts.append(task.description)
            training_task_ids.append(task.task_id)
        
        # Add sample prompts with their expected tasks
        for prompt_data in SAMPLE_PROMPTS:
            for task_id in prompt_data["expected_tasks"]:
                training_texts.append(prompt_data["text"])
                training_task_ids.append(task_id)
        
        self.task_descriptions = training_texts
        self.task_ids = training_task_ids
        self.task_vectors = self.vectorizer.fit_transform(training_texts)
    
    def map_prompt_to_tasks(self, prompt: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Map a user prompt to relevant tasks with confidence scores
        
        Args:
            prompt: User input text
            threshold: Minimum confidence score for task matching
            
        Returns:
            List of (task_id, confidence_score) tuples
        """
        # Vectorize the input prompt
        prompt_vector = self.vectorizer.transform([prompt])
        
        # Calculate similarity with all task descriptions
        similarities = cosine_similarity(prompt_vector, self.task_vectors).flatten()
        
        # Get tasks above threshold
        matched_tasks = []
        for i, similarity in enumerate(similarities):
            if similarity >= threshold:
                task_id = self.task_ids[i]
                matched_tasks.append((task_id, similarity))
        
        # Remove duplicates and sort by confidence
        unique_tasks = {}
        for task_id, score in matched_tasks:
            if task_id not in unique_tasks or score > unique_tasks[task_id]:
                unique_tasks[task_id] = score
        
        # Sort by confidence score (descending)
        result = [(task_id, score) for task_id, score in unique_tasks.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    def get_task_by_id(self, task_id: str) -> Task:
        """Get task object by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_persona(self, persona: PersonaType) -> List[Task]:
        """Get all tasks associated with a persona"""
        return [task for task in TASKS if task.persona == persona]
    
    def analyze_prompt_keywords(self, prompt: str) -> Dict[str, List[str]]:
        """
        Analyze prompt for specific keywords that indicate task types
        """
        prompt_lower = prompt.lower()
        
        keyword_mapping = {
            TaskType.FEATURE_DEVELOPMENT: [
                'implement', 'develop', 'create', 'build', 'add', 'new feature',
                'enhancement', 'functionality', 'code', 'application'
            ],
            TaskType.PRODUCTION_SUPPORT: [
                'production', 'server down', 'error', 'bug', 'hotfix', 'debug',
                'issue', 'problem', 'fix', 'logs', 'crash'
            ],
            TaskType.INCIDENT_RESOLUTION: [
                'ticket', 'incident', 'troubleshoot', 'investigate', 'resolve',
                'network', 'connectivity', 'outage', 'itsm'
            ],
            TaskType.INFRASTRUCTURE_MAINTENANCE: [
                'maintenance', 'script', 'configuration', 'server', 'infrastructure',
                'update', 'patch', 'system'
            ],
            TaskType.LEAD_GENERATION: [
                'lead', 'prospect', 'research', 'campaign', 'outbound',
                'client', 'customer', 'sales'
            ],
            TaskType.PROPOSAL_DEVELOPMENT: [
                'proposal', 'collateral', 'presentation', 'meeting',
                'client', 'pitch', 'document'
            ]
        }
        
        found_keywords = {}
        for task_type, keywords in keyword_mapping.items():
            matches = [kw for kw in keywords if kw in prompt_lower]
            if matches:
                found_keywords[task_type.value] = matches
        
        return found_keywords
