from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import shutil
import uuid
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class FileMetadata(BaseModel):
    id: str
    filename: str
    size: int
    content_type: str
    uploaded_at: str
    
class FileListResponse(BaseModel):
    files: List[FileMetadata]
    
class FileUploadResponse(BaseModel):
    id: str
    filename: str
    size: int
    content_type: str
    
# --- Configuration ---
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Helper Functions ---
def get_file_metadata(file_id: str) -> Optional[FileMetadata]:
    """Get metadata for a specific file."""
    file_path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.exists(file_path):
        return None
        
    # Get file info
    original_filename = None
    content_type = None
    uploaded_at = None
    
    # Read metadata file if it exists
    metadata_path = f"{file_path}.meta"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = f.read().strip().split("\n")
                if len(metadata) >= 3:
                    original_filename = metadata[0]
                    content_type = metadata[1]
                    uploaded_at = metadata[2]
        except Exception as e:
            logger.error(f"Error reading metadata for file {file_id}: {str(e)}")
    
    # Use defaults if metadata is missing
    if not original_filename:
        original_filename = file_id
    if not content_type:
        content_type = "application/octet-stream"
    if not uploaded_at:
        uploaded_at = datetime.now().isoformat()
        
    # Get file size
    size = os.path.getsize(file_path)
    
    return FileMetadata(
        id=file_id,
        filename=original_filename,
        size=size,
        content_type=content_type,
        uploaded_at=uploaded_at
    )

# --- Endpoints ---
@router.get("/", response_model=FileListResponse)
async def list_files():
    """List all uploaded files."""
    files = []
    
    # List files in upload directory
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            # Skip metadata files
            if filename.endswith(".meta"):
                continue
                
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                metadata = get_file_metadata(filename)
                if metadata:
                    files.append(metadata)
    
    return FileListResponse(files=files)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """Upload a file to the server."""
    try:
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the file
        file_path = os.path.join(UPLOAD_DIR, file_id)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Save metadata
        with open(f"{file_path}.meta", "w") as f:
            f.write(f"{file.filename}\n")
            f.write(f"{file.content_type}\n")
            f.write(f"{datetime.now().isoformat()}\n")
            if description:
                f.write(f"{description}\n")
                
        return FileUploadResponse(
            id=file_id,
            filename=file.filename,
            size=file_size,
            content_type=file.content_type or "application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading the file: {str(e)}"
        )
        
@router.get("/{file_id}")
async def download_file(file_id: str):
    """Download a file by its ID."""
    file_path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found"
        )
        
    # Get metadata
    metadata = get_file_metadata(file_id)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving file metadata"
        )
        
    return FileResponse(
        path=file_path,
        filename=metadata.filename,
        media_type=metadata.content_type
    )
    
@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete a file by its ID."""
    file_path = os.path.join(UPLOAD_DIR, file_id)
    metadata_path = f"{file_path}.meta"
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found"
        )
        
    try:
        # Delete the file
        os.remove(file_path)
        
        # Delete metadata if it exists
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"File '{file_id}' deleted successfully"}
        )
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the file: {str(e)}"
        ) 