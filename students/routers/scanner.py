# backend/students/routers/scanner.py
from ninja import Router, File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404

from students.models import DocumentUploadSession, HscapCandidate

router = Router()

# 1. Clerk initiates this from the PC (Inherits global JWT auth from master router)
@router.post("/init", response={200: dict})
def init_scanner_session(request, candidate_id: int, doc_type: str):
    candidate = get_object_or_404(HscapCandidate, id=candidate_id, school=request.auth.employee_profile.school)
    session = DocumentUploadSession.objects.create(candidate=candidate, document_type=doc_type)
    return 200, {"session_id": str(session.id)}

# 2. Public endpoint used by both PC and Mobile Phone
@router.get("/status/{session_id}", response={200: dict, 404: dict}, auth=None)
def check_scanner_status(request, session_id: str):
    session = get_object_or_404(DocumentUploadSession.objects.select_related('candidate'), id=session_id)
    if session.is_expired():
        return 404, {"detail": "Session expired."}
    
    # Pack up non-sensitive administrative metrics to confirm target on phone
    return 200, {
        "status": "completed" if session.is_completed else "pending",
        "file_url": session.scanned_file.url if session.is_completed and session.scanned_file else None,
        "candidate": {
            "name": session.candidate.name,
            "app_num": session.candidate.app_num,
            "reg_num": session.candidate.reg_num,
            "document_type_label": "Transfer Certificate (TC)" if session.document_type == "tc" else "Conduct Certificate"
        }
    }

# 3. Public endpoint used by Mobile Phone to submit data
@router.post("/upload/{session_id}", response={200: dict, 400: dict}, auth=None) # 👈 ENSURE auth=None IS HERE
def mobile_upload(request, session_id: str, file: UploadedFile = File(...)):
    session = get_object_or_404(DocumentUploadSession, id=session_id)
    if session.is_expired() or session.is_completed:
        return 400, {"detail": "Session invalid or expired."}
        
    session.scanned_file = file
    session.is_completed = True
    session.save()
    return 200, {"detail": "File secured successfully."}