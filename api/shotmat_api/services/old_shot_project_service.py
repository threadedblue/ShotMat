import D4M.assoc as d4m_assoc
from typing import List, Dict, Any, Optional
from constants import SHOT_EVENT_HEADER, PROJECT_HEADER, DELIMITER

# Define a key to store the shots Assoc within the project Assoc
SHOTS_ASSOC_KEY = "shots_data" # This key will hold the Assoc object containing all shots

def create_project(project_name): 
    """
    Creates a new project structure as a D4M Assoc array. 
    The main Assoc holds project-level metadata, including a nested Assoc for shots.
    """
    # Define columns for the project-level Assoc (e.g., project_name, and a key for the shots Assoc)
    project_cols = ["project_name", SHOTS_ASSOC_KEY]
    
    # Create the main project Assoc. Its single row key is the project_name.
    project_assoc = d4m_assoc.Assoc(project_name, ','.join(project_cols), '')
    
    # Define columns for the nested shots Assoc (these are the attributes of each shot)
    # We include 'n_prompt' here, assuming it's a desired attribute for shots,
    # even if not explicitly in PROJECT_HEADER yet.
    shot_attributes = PROJECT_HEADER.split(DELIMITER)
    if "n_prompt" not in shot_attributes:
        shot_attributes.append("n_prompt") # Ensure n_prompt is a recognized column for shots
        
    # Create an empty Assoc for the shots themselves.
    # Its row keys will be shot_ids, and columns will be shot attributes.
    # Initialize with an empty row key and the shot attribute columns.
    empty_shots_assoc = d4m_assoc.Assoc('', ','.join(shot_attributes), '')
    
    # Store the empty shots Assoc within the project_assoc
    project_assoc.set(project_name, SHOTS_ASSOC_KEY, empty_shots_assoc)
    
    return project_assoc

def assoc_to_json_structure(project_assoc: d4m_assoc.Assoc) -> Dict[str, Any]:
    """
    Converts a D4M Assoc object representing a project (with nested shots Assoc)
    into a structured JSON format.
    """
    # The project_assoc is expected to have the project_name as its single row key.
    project_name = project_assoc.row
     
    # Retrieve the nested shots Assoc from within the project_assoc
    # This Assoc is expected to have shot_ids as row keys and shot attributes as columns.
    shots_assoc = project_assoc.get(project_name, SHOTS_ASSOC_KEY)
    
    serialized_shots = []
    
    # Define the keys we want in the final JSON output for each shot.
    # This list includes 'n_prompt' as requested by the user.
    shot_output_keys = ["shot_id", "generator", "prompt", "n_prompt", "input", "output"]
    
    # Iterate through each row of the shots_assoc. Each row key is a shot_id.
    # If shots_assoc is empty, shots_assoc.rows() will return an empty list.
    for shot_id in shots_assoc.rows():
        shot_data = {}
        shot_data["shot_id"] = shot_id # The row key is the shot_id
        
        for key in shot_output_keys:
            if key == "shot_id":
                continue # Already handled as the row key
            
            # Retrieve the value for the current shot_id and key.
            # D4M.assoc.get typically returns None if the key combination doesn't exist.
            value = shots_assoc.get(shot_id, key)
            
            # Ensure all values are strings, defaulting to empty string if None.
            shot_data[key] = str(value) if value is not None else ""
        
        serialized_shots.append(shot_data)
        
    json_output = {
        "projectName": project_name,
        "shots": serialized_shots
    }
    return json_output