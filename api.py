import requests
import json
from typing import Dict, List, Optional, Union, Any
import os

# Base URL for the API
BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')

# Project API functions

def create_project(project_name: str) -> Dict[str, Any]:
    """
    Create a new project
    
    Args:
        project_name: Name of the project
        
    Returns:
        Project data including project_id, project_name, and created_at
    """
    url = f"{BASE_URL}/projects/"
    payload = {"project_name": project_name}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating project: {e}")
        return {}

def get_projects(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get a list of all projects with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of projects
    """
    url = f"{BASE_URL}/projects/"
    params = {"skip": skip, "limit": limit}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}")
        return []

def get_project(project_id: int) -> Dict[str, Any]:
    """
    Get a specific project by ID
    
    Args:
        project_id: ID of the project to retrieve
        
    Returns:
        Project data
    """
    url = f"{BASE_URL}/projects/{project_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching project {project_id}: {e}")
        return {}

def update_project(project_id: int, project_name: str) -> Dict[str, Any]:
    """
    Update a project
    
    Args:
        project_id: ID of the project to update
        project_name: New name for the project
        
    Returns:
        Updated project data
    """
    url = f"{BASE_URL}/projects/{project_id}"
    payload = {"project_name": project_name}
    
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating project {project_id}: {e}")
        return {}

def delete_project(project_id: int) -> bool:
    """
    Delete a project
    
    Args:
        project_id: ID of the project to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    url = f"{BASE_URL}/projects/{project_id}"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting project {project_id}: {e}")
        return False

def get_project_with_counts(project_id: int) -> Dict[str, Any]:
    """
    Get a project with counts of related entities (base maps, defects, users)
    
    Args:
        project_id: ID of the project
        
    Returns:
        Project data with counts
    """
    url = f"{BASE_URL}/projects/{project_id}/with-counts"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching project with counts {project_id}: {e}")
        return {}

def get_user_projects(user_id: int) -> Dict[str, Any]:
    """
    Get a user with their projects and roles
    
    Args:
        user_id: ID of the user
        
    Returns:
        User data with projects and roles
    """
    url = f"{BASE_URL}/users/{user_id}/projects"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects for user {user_id}: {e}")
        return {}