import json
import os
from threading import Lock

DATA_STORE_PATH = '/Users/gcr/ShotMat.Wk/shotmat/data_store/common/shot_events.json'

# A lock to ensure thread-safe writes to the JSON file.
file_lock = Lock()

def assoc_to_json_structure(shot_event_data: dict):
    """
    Adds a new shot event to the shot_events.json data store.

    This function reads the existing shot events, appends the new one,
    and writes the entire structure back to the file. It will create the
    file and directory structure if they do not exist. This operation
    is thread-safe.

    Args:
        shot_event_data (dict): A dictionary representing the new shot event.
                                It should conform to the shot event schema,
                                e.g., {'name': '...', 'service': '...', 'params': {...}}.
    """
    with file_lock:
        data = {"shot_events": []}
        try:
            # Ensure the directory exists before trying to read/write the file.
            os.makedirs(os.path.dirname(DATA_STORE_PATH), exist_ok=True)

            if os.path.exists(DATA_STORE_PATH) and os.path.getsize(DATA_STORE_PATH) > 0:
                with open(DATA_STORE_PATH, 'r') as f:
                    try:
                        data = json.load(f)
                        # Ensure the root 'shot_events' key exists.
                        if 'shot_events' not in data or not isinstance(data['shot_events'], list):
                            data['shot_events'] = []
                    except json.JSONDecodeError:
                        # File is corrupt or empty, start with a fresh structure.
                        pass # data is already initialized

        except IOError as e:
            # Handle potential read errors, though os.makedirs reduces this risk.
            print(f"Error accessing data store: {e}")
            # Proceed with the default empty structure.

        # Append the new shot event
        data['shot_events'].append(shot_event_data)

        # Write the updated data back to the file
        with open(DATA_STORE_PATH, 'w') as f:
            json.dump(data, f, indent=4)