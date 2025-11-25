import os
from fastapi import APIRouter, HTTPException

from ..services import shot_events_service

router = APIRouter()

@router.post("/shot_event_request")
def shot_event_service():
    """
    Loads the shot_events.tsv file and returns its contents
    in a structured JSON format for the UI.
    """
    try:
        # Construct the path to the TSV file relative to the project root.
        # This assumes the API is run from within the ShotMat.Wk directory or similar.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up to the shotmat project root
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        file_path = os.path.join(project_root, 'data_store/common/shot_events.tsv')

        # Load the TSV file into a D4M Assoc object
        assoc_data = shot_events_service.load_matrix_tsv_to_assoc(file_path)

        if assoc_data is None:
            raise HTTPException(status_code=404, detail=f"Data file not found at {file_path}")

        # Convert the Assoc object to the desired JSON structure for the UI
        json_output = shot_events_service.assoc_to_json_structure(assoc_data)
        return json_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")