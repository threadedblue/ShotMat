import os
from fastapi import APIRouter, HTTPException

from ..services import shot_project_service

router = APIRouter()

@router.post("/shot_project_request")

def shot_project_service(project_name):
    
    shot_project_service.create_project()