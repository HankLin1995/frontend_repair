import requests
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

def create_project_image(project_id: int, image) -> Dict[str, Any]:
    """
    Create a new project image

    Args:
        project_id: ID of the project
        image: Streamlit UploadedFile

    Returns:
        Image data including image_id, project_id, and image_path
    """

    url = f"{BASE_URL}/projects/{project_id}/image"

    try:
        response=requests.post(url,files=image)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating project image: {e}")
        return {}
    except Exception as e:
        print(f"File error: {e}")
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

def get_project_with_roles(project_id: int) -> Dict[str, Any]:
    """
    Get a project with roles of related entities (users)
    
    Args:
        project_id: ID of the project
        
    Returns:
        Project data with roles
    """
    url = f"{BASE_URL}/projects/{project_id}/with-roles"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching project roles {project_id}: {e}")
        return {}

#-----權限------

def create_permission(project_id: int, user_email: str, user_role: str) -> Dict[str, Any]:
    """
    Create a new permission for a user on a project
    
    Args:
        project_id: ID of the project
        user_id: ID of the user
        user_role: Role of the user (e.g., "owner", "member")
        
    Returns:
        Permission data including permission_id, project_id, user_id, and role
    """
    url = f"{BASE_URL}/permissions/"
    payload = {"project_id": project_id, "user_email": user_email, "user_role": user_role}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating permission: {e}")
        return {}

def get_permissions(project_id: int):
    url = f"{BASE_URL}/permissions/?project_id={project_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching permissions: {e}")
        return []

def get_project_by_email(user_email: str):
    url = f"{BASE_URL}/permissions/?user_email={user_email}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching project by email: {e}")
        return []

def delete_permission(permission_id: int):
    url = f"{BASE_URL}/permissions/{permission_id}"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting permission {permission_id}: {e}")
        return False

def update_permission(permission_id: int, user_role: str):
    url = f"{BASE_URL}/permissions/{permission_id}"
    payload = {"user_role": user_role}
    
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating permission {permission_id}: {e}")
        return {}

#-------用戶--------

def get_users():
    url = f"{BASE_URL}/users/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users: {e}")
        return []

def create_user(user_name: str, user_email: str, user_role: str, phone: str = "", line_id: str = "") -> dict:
    """
    Create a new user
    """
    url = f"{BASE_URL}/users/"
    payload = {
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "phone": phone,
        "line_id": line_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating user: {e}")
        return {}

def update_user(user_id: int, user_name: str, user_email: str, user_role: str, phone: str = "", line_id: str = "") -> dict:
    """
    Update an existing user
    """
    url = f"{BASE_URL}/users/{user_id}"
    payload = {
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "phone": phone,
        "line_id": line_id
    }
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating user {user_id}: {e}")
        return {}

def delete_user(user_id: int) -> bool:
    """
    Delete a user by ID
    """
    url = f"{BASE_URL}/users/{user_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting user {user_id}: {e}")
        return False

#-------廠商--------
def get_vendors():
    url = f"{BASE_URL}/vendors/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching vendors: {e}")
        return []

def create_vendor(project_id: int,vendor_name: str, contact_person: str, phone: str,email:str,line_id:str, responsibilities: str) -> Dict[str, Any]:
    """
    Create a new vendor
    
    Args:
        project_id: ID of the project
        vendor_name: Name of the vendor
        contact_person: Contact person of the vendor
        phone: Phone number of the vendor
        responsibilities: Responsibilities of the vendor
        
    Returns:
        Vendor data including vendor_id, vendor_name, contact_person, phone, and responsibilities
    """
    url = f"{BASE_URL}/vendors/"
    payload = {"project_id": project_id,"vendor_name": vendor_name, "contact_person": contact_person, "phone": phone,"email":email,"line_id":line_id,"responsibilities":responsibilities}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating vendor: {e}")
        return {}

def update_vendor(vendor_id: int, vendor_name: str, contact_person: str, phone: str,email:str,line_id:str, responsibilities: str) -> Dict[str, Any]:
    """
    Update an existing vendor
    
    Args:
        vendor_id: ID of the vendor to update
        vendor_name: New name of the vendor
        contact_person: New contact person of the vendor
        phone: New phone number of the vendor
        responsibilities: New responsibilities of the vendor
        
    Returns:
        Updated vendor data including vendor_id, vendor_name, contact_person, phone, and responsibilities
    """
    url = f"{BASE_URL}/vendors/{vendor_id}"
    payload = {"vendor_name": vendor_name, "contact_person": contact_person, "phone": phone,"email":email,"line_id":line_id,"responsibilities":responsibilities}
    
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating vendor {vendor_id}: {e}")
        return {}

def delete_vendor(vendor_id: int):
    url = f"{BASE_URL}/vendors/{vendor_id}"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting vendor {vendor_id}: {e}")
        return False


#--------取得缺失分類---------

def get_defect_categories():
    url = f"{BASE_URL}/defect-categories/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching defect categories: {e}")
        return []
    

def create_defect_category(project_id: int, category_name: str, description: str) -> Dict[str, Any]:
    """
    Create a new defect category
    
    Args:
        project_id: ID of the project
        category_name: Name of the category
        
    Returns:
        Category data including category_id, category_name, and created_at
    """
    url = f"{BASE_URL}/defect-categories/"
    payload = {"project_id": project_id,"category_name": category_name,"description":description}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating category: {e}")
        return {}

def update_defect_category(defect_category_id: int, category_name: str, description: str) -> dict:
    """
    Update an existing defect category
    """
    url = f"{BASE_URL}/defect-categories/{defect_category_id}"
    payload = {"category_name": category_name,"description":description}
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating defect category {defect_category_id}: {e}")
        return {}

def delete_defect_category(defect_category_id: int) -> bool:
    """
    Delete a defect category by ID
    """
    url = f"{BASE_URL}/defect-categories/{defect_category_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting defect category {defect_category_id}: {e}")
        return False

def create_basemap(project_id: int, map_name: str, file_path: str="file_path") -> dict:
    """
    Create a new basemap
    """
    url = f"{BASE_URL}/base-maps/"
    payload = {"project_id": project_id, "map_name": map_name, "file_path": file_path}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating basemap: {e}")
        return {}

def get_basemap(basemap_id: int):
    url = f"{BASE_URL}/base-maps/{basemap_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching basemap: {e}")
        return []

def get_basemaps(project_id: int):
    url = f"{BASE_URL}/base-maps/?project_id={project_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching basemaps: {e}")
        return []

def create_basemap_image(basemap_id: int, files) -> Dict[str, Any]:
    """
    Create a new basemap image

    Args:
        basemap_id: ID of the basemap
        files: dict, e.g. {"image": (filename, bytes, content_type)}

    Returns:
        Image data including image_id, project_id, and image_path
    """

    url = f"{BASE_URL}/base-maps/{basemap_id}/image"

    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating basemap image: {e}")
        return {}
    except Exception as e:
        print(f"File error: {e}")
        return {}


def update_basemap(basemap_id: int, map_name: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/base-maps/{basemap_id}"
    payload = {"map_name": map_name}
    
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating basemap {basemap_id}: {e}")
        return {}

def delete_basemap(basemap_id: int) -> bool:
    url = f"{BASE_URL}/base-maps/{basemap_id}"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting basemap {basemap_id}: {e}")
        return False


def create_defect(project_id: int,user_id:int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new defect
    
    Args:
        project_id: ID of the project
        user_id: ID of the user
        data: Dictionary containing defect data
            - defect_description: Description of the defect
            - defect_category_id: ID of the defect category (optional)
            - assigned_vendor_id: ID of the assigned vendor (optional)
            - expected_completion_day: Expected completion day (optional)
            - status: Status of the defect (optional)
            
    Returns:
        Defect data including defect_id
    """
    url = f"{BASE_URL}/defects/"

    # Prepare the payload
    payload = {
        "project_id": project_id,
        "submitted_id": user_id,  # Using project_id as submitted_id for now
        "defect_description": data.get("defect_description", ""),
        "defect_category_id": data.get("defect_category_id"),
        "assigned_vendor_id": data.get("assigned_vendor_id"),
        "previous_defect_id": data.get("previous_defect_id"),
        "status": "改善中",
    }

    # print(payload)

    # Add expected completion day if provided
    if data.get("expected_date"):
        # data['expected_date'] is likely a datetime.date object from Streamlit
        try:
            from datetime import datetime, date
            if isinstance(data["expected_date"], date):
                expected_date = datetime.combine(data["expected_date"], datetime.min.time())
            else:
                expected_date = datetime.strptime(data["expected_date"], "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            delta = (expected_date - today).days
            payload["expected_completion_day"] = delta
        except Exception as e:
            print(f"Error calculating expected completion days: {e}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating defect: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response content: {e.response.content}")
        return {}


def create_defect_mark(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new defect mark
    
    Args:
        defect_id: ID of the defect
        data: Dictionary containing defect mark data
            - base_map_id: ID of the base map
            - coordinate_x: X coordinate
            - coordinate_y: Y coordinate
            - scale: Scale (default: 1.0)
            
    Returns:
        Defect mark data including defect_mark_id
    """
    url = f"{BASE_URL}/defect-marks/"
    
    # Prepare the payload
    # payload = {
    #     "defect_form_id": defect_id,
    #     "base_map_id": data.get("basemap_id"),
    #     "coordinate_x": data.get("basemap_mark_X", 0),
    #     "coordinate_y": data.get("basemap_mark_Y", 0),
    #     "scale": data.get("scale", 1.0)
    # }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating defect mark: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response content: {e.response.content}")
        return {}


def upload_defect_image(defect_id: int, image_file, description: str = "") -> Dict[str, Any]:
    """
    Upload an image for a defect (using /photos/ endpoint)
    Args:
        defect_id: ID of the defect
        image_file: Image file to upload (should be file-like object or tuple)
        description: Description for the image
    Returns:
        Image data including image_id
    """
    url = f"{BASE_URL}/photos/"
    try:
        files = {
            "file": image_file  # image_file can be (filename, fileobj, mimetype) or file-like
        }
        data = {
            "related_type": "defect",
            "related_id": str(defect_id),
            "description": description or ""
        }
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading defect image: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response content: {e.response.content}")
        return {}

def get_defects(project_id: int):
    url = f"{BASE_URL}/defects/?project_id={project_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching defects: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response content: {e.response.content}")
        return []
        
