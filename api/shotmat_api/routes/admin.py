from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict

from ..services import shot_project_service, shot_events_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

class ProjectRequest(BaseModel):
    project_name: str

class ShotEventRequest(BaseModel):
    # Define the fields for a shot event based on your data model
    # Example:
    shot_id: str
    generator: str
    prompt: str
    n_prompt: str
    input: str
    output: str

# --- Shot Project CRUD ---

@router.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(project_request: ProjectRequest) -> Dict[str, Any]:
    """
    Creates a new project.
    """
    project_assoc = shot_project_service.create_project(project_request.project_name)
    return shot_project_service.assoc_to_json_structure(project_assoc)

@router.get("/projects/{project_name}")
def get_project(project_name: str):
    """
    Retrieves a specific project's details.
    (Placeholder: Needs implementation to load a project from storage)
    """
    # TODO: Implement service logic to find and load a project by name
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Get project not implemented")

@router.put("/projects/{project_name}")
def update_project(project_name: str, project_data: Dict[Any, Any] = Body(...)):
    """
    Updates a project.
    (Placeholder: Needs implementation to update a project in storage)
    """
    # TODO: Implement service logic to update a project
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Update project not implemented")

@router.delete("/projects/{project_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_name: str):
    """
    Deletes a project.
    (Placeholder: Needs implementation to delete a project from storage)
    """
    # TODO: Implement service logic to delete a project
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Delete project not implemented")

# --- Shot Events Data Retrieval ---

@router.get("/events")
def get_all_shot_events():
    """
    Loads the shot_events.tsv file and returns its contents
    in a structured JSON format.
    """
    try:
        # Construct the path to the TSV file relative to the project root.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up from routes -> shotmat_api -> api -> shotmat -> ShotMat.Wk
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
        file_path = os.path.join(project_root, 'data_store/common/shot_events.tsv')

        assoc_data = shot_events_service.load_matrix_tsv_to_assoc(file_path)
        if assoc_data is None:
            raise HTTPException(status_code=404, detail=f"Data file not found at {file_path}")

        json_output = shot_events_service.assoc_to_json_structure(assoc_data)
        return json_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# --- Shot Event CRUD ---
# These would likely operate on the shot_events.tsv file or a database.

@router.post("/events", status_code=status.HTTP_201_CREATED)
def create_shot_event(event: ShotEventRequest):
    """
    Adds a new shot event.
    (Placeholder: Needs implementation to add an event to storage)
    """
    # TODO: Implement service logic to add a new shot event
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Create shot event not implemented")

@router.get("/events/{shot_id}", response_model=ShotEventRequest)
def get_shot_event(shot_id: str):
    """
    Retrieves a specific shot event by its ID.
    (Placeholder: Needs implementation to find and return an event from storage)
    """
    # TODO: Implement service logic to find and return a shot event by its ID
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Get shot event not implemented")

@router.put("/events/{shot_id}", response_model=ShotEventRequest)
def update_shot_event(shot_id: str, event: ShotEventRequest):
    """
    Updates an existing shot event.
    (Placeholder: Needs implementation to find and update an event in storage)
    """
    # TODO: Implement service logic to update a shot event
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Update shot event not implemented")

@router.delete("/events/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shot_event(shot_id: str):
    """
    Deletes a shot event by its ID.
    (Placeholder: Needs implementation to delete an event from storage)
    """
    # TODO: Implement service logic to delete a shot event
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Delete shot event not implemented")