import os
import json
import uuid
from typing import Any, Dict, List

from pydantic import BaseModel, Field

# Assuming d4m_assoc is available in the environment.
# If it's in a specific package, the import might need adjustment.
import D4M.assoc as d4m_assoc

# --- Data Models ---

class Shot(BaseModel):
    """Represents a single shot within a project."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_text: str
    mlx_args: Dict[str, Any]
    output_url: str

class ShotProject(BaseModel):
    """Represents a full project, containing a list of shots."""
    project_name: str
    shots: List[Shot]

# --- Service Implementation ---

class ProjectService:
    """
    Service class for managing Shot Projects, including loading, saving,
    and modifying shots.
    """
    _TSV_FILENAME = "project.tsv"
    _MEDIA_SUBDIR = "media"
    _TSV_COLUMNS = ["shot_id", "input_text", "mlx_args_json", "output_url"]

    def __init__(self, project_root: str):
        """
        Initializes the service with the root directory for all projects.

        Args:
            project_root: The absolute path to the directory containing all project folders.
        """
        if not project_root:
            raise ValueError("project_root cannot be empty.")
        self.project_root = project_root

    def _get_project_dir(self, project_name: str) -> str:
        return os.path.join(self.project_root, project_name)

    def _get_project_tsv_path(self, project_name: str) -> str:
        return os.path.join(self._get_project_dir(project_name), self._TSV_FILENAME)

    def load_project(self, project_name: str) -> ShotProject:
        """
        Reads project.tsv using d4m_assoc.readcsv and returns a ShotProject model.

        Raises:
            FileNotFoundError: If the project's TSV file does not exist.
            ValueError: If the TSV is malformed or missing required columns.
        """
        tsv_path = self._get_project_tsv_path(project_name)
        if not os.path.exists(tsv_path):
            raise FileNotFoundError(f"Project '{project_name}' not found at {tsv_path}")

        try:
            # Use d4m_assoc.readcsv to load the TSV into an Assoc object
            assoc = d4m_assoc.readcsv(tsv_path)
        except Exception as e:
            raise ValueError(f"Failed to parse TSV file at {tsv_path}: {e}")

        shots = []
        # The row keys of the Assoc are the shot_ids
        for shot_id in assoc.rows():
            try:
                mlx_args_json = assoc.get(shot_id, "mlx_args_json")
                shots.append(Shot(
                    id=shot_id,
                    input_text=assoc.get(shot_id, "input_text") or "",
                    mlx_args=json.loads(mlx_args_json) if mlx_args_json else {},
                    output_url=assoc.get(shot_id, "output_url") or ""
                ))
            except (json.JSONDecodeError, KeyError) as e:
                raise ValueError(f"Malformed data for shot_id '{shot_id}' in {tsv_path}: {e}")

        return ShotProject(project_name=project_name, shots=shots)

    def save_project(self, project: ShotProject) -> None:
        """
        Persists the ShotProject model to project.tsv using d4m_assoc.writecsv.
        Ensures project and media directories exist.
        """
        project_dir = self._get_project_dir(project.project_name)
        os.makedirs(project_dir, exist_ok=True)

        # Create an empty Assoc with the correct columns
        assoc = d4m_assoc.Assoc('', ','.join(self._TSV_COLUMNS), '')

        for shot in project.shots:
            # The row key is the shot ID
            row_key = shot.id
            assoc.set(row_key, "shot_id", shot.id)
            assoc.set(row_key, "input_text", shot.input_text)
            assoc.set(row_key, "mlx_args_json", json.dumps(shot.mlx_args))
            assoc.set(row_key, "output_url", shot.output_url)

        tsv_path = self._get_project_tsv_path(project.project_name)
        d4m_assoc.writecsv(assoc, tsv_path)

    def add_shot(
        self,
        project_name: str,
        input_text: str,
        mlx_args: Dict[str, Any],
        image_bytes: bytes,
        image_ext: str = ".png",
    ) -> Shot:
        """
        Creates a new Shot, saves its media artifact, updates the project TSV,
        and returns the new Shot model.
        """
        try:
            project = self.load_project(project_name)
        except FileNotFoundError:
            # If project doesn't exist, create a new one in memory
            project = ShotProject(project_name=project_name, shots=[])

        new_shot = Shot(input_text=input_text, mlx_args=mlx_args, output_url="")

        # Save the media file
        media_dir = os.path.join(self._get_project_dir(project_name), self._MEDIA_SUBDIR)
        os.makedirs(media_dir, exist_ok=True)
        
        filename = f"{new_shot.id}{image_ext}"
        image_path = os.path.join(media_dir, filename)
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        # Set the public-facing URL for the shot
        new_shot.output_url = f"/media/{project_name}/{filename}"

        # Add the new shot to the project and save
        project.shots.append(new_shot)
        self.save_project(project)

        return new_shot

    def delete_shot(self, project_name: str, shot_id: str) -> None:
        """
        Removes a shot from the project's TSV and deletes its associated media file.
        """
        project = self.load_project(project_name)

        shot_to_delete = next((s for s in project.shots if s.id == shot_id), None)
        if not shot_to_delete:
            return # Shot not found, nothing to do

        # Remove the shot from the list
        project.shots = [s for s in project.shots if s.id != shot_id]
        self.save_project(project)

        # Optionally, delete the associated media file
        if shot_to_delete.output_url:
            # Convert URL path to filesystem path
            # Example URL: /media/my_project/shot1.png
            relative_path = shot_to_delete.output_url.strip('/')
            file_path = os.path.join(self.project_root, relative_path)
            if os.path.exists(file_path):
                os.remove(file_path)