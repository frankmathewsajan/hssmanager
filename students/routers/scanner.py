from ninja import Router, File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth

from students.models import DocumentUploadSession, HscapCandidate

# Notice we don't need tags or auth here, the Master Assembler will apply them
router = Router()

@router.post("/init", response={200: dict})
def init_scanner_session(request, candidate_id: int, doc_type: str):
    """PC requests a secure QR session."""
    candidate = get_object_or_404(HscapCandidate, id=candidate_id, school=request.auth.employee_profile.school)
    session = DocumentUploadSession.objects.create(candidate=candidate, document_type=doc_type)
    return 200, {"session_id": str(session.id)}

@router.get("/status/{session_id}", response={200: dict, 404: dict})
def check_scanner_status(request, session_id: str):
    """PC polls this every 2 seconds."""
    session = get_object_or_404(DocumentUploadSession, id=session_id)
    if session.is_expired():
        return 404, {"detail": "Session expired."}
    if session.is_completed:
        return 200, {"status": "completed", "file_url": session.scanned_file.url}
    return 200, {"status": "pending"}

@router.post("/upload/{session_id}", response={200: dict, 400: dict}, auth=None) # Mobile might not have JWT
def mobile_upload(request, session_id: str, file: UploadedFile = File(...)):
    """Mobile phone POSTs the photo here."""
    session = get_object_or_404(DocumentUploadSession, id=session_id)
    if session.is_expired() or session.is_completed:
        return 400, {"detail": "Session invalid or expired."}
        
    session.scanned_file = file
    session.is_completed = True
    session.save()
    return 200, {"detail": "File secured successfully."}