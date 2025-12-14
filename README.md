# Task-Based Access Pattern Model

## Overview
A GenAI application that implements task-based access control by mapping user prompts to tasks, tasks to personas, and enforcing appropriate permissions for GitHub and file system access.

## Architecture
- **Prompt Analysis**: Natural language processing to extract intent and map to predefined tasks
- **Task Classification**: Categorize tasks by type (Feature Development, Production Support, etc.)
- **Persona Mapping**: Associate tasks with appropriate personas and their permissions
- **Access Control**: Enforce permissions for GitHub (R/W for Engineering, R for IT) and file system access

## Personas
- **Alex (Engineering)**: GitHub R/W, Engineering files, focuses on feature development and production support
- **Priya (IT)**: GitHub R, IT files, handles ITSM tickets and infrastructure maintenance  
- **Marco (Sales)**: Sales files only, drives campaigns and proposal development

## Setup
```bash
pip install -r requirements.txt
python main.py
```