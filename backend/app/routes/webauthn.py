from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.database import get_database
from app.schemas.webauthn import WebAuthnRegisterOptions, WebAuthnAuthenticateOptions
from app.utils.webauthn import WebAuthnService
from app.utils.security import decode_token
import base64
from typing import Optional

router = APIRouter(prefix="/api/webauthn", tags=["webauthn"])


def get_current_student(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current authenticated student"""
    db = get_database()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = authorization.split(" ", 1)[1]
    token_data = decode_token(token)

    if not token_data or token_data.role != "student":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    student = db["students"].find_one({"student_id": int(token_data.sub)})
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.post("/register/options", response_model=WebAuthnRegisterOptions)
async def get_webauthn_register_options(
    current_student: dict = Depends(get_current_student)
):
    """Get WebAuthn registration options"""
    
    if current_student.get("biometric_registered"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biometric already registered for this student"
        )
    
    options = WebAuthnService.generate_registration_options(
        user_id=current_student["student_id"],
        username=current_student["email"],
        user_display_name=current_student["full_name"]
    )
    
    # Store challenge in session (in production, use Redis or database)
    # For now, we'll pass it to client and expect it back
    
    return WebAuthnRegisterOptions(**options)


@router.post("/register/verify")
async def verify_webauthn_registration(
    payload: dict,
    current_student: dict = Depends(get_current_student)
):
    """Verify WebAuthn registration response"""

    db = get_database()
    response = payload.get("response")
    challenge = payload.get("challenge")
    if not response or not challenge:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration payload")

    challenge_bytes = base64.b64decode(challenge)
    
    result = WebAuthnService.verify_registration(
        credential_id=response.get("rawId", ""),
        client_data_json=response.get("response", {}).get("clientDataJSON", ""),
        attestation_object=response.get("response", {}).get("attestationObject", ""),
        challenge=challenge_bytes
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration verification failed"
        )
    
    # Check if credential already exists
    existing = db["webauthn_credentials"].find_one({
        "credential_id": result["credential_id"]
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This credential is already registered"
        )
    
    # Store credential
    credential = {
        "credential_id": result["credential_id"],
        "student_id": current_student["student_id"],
        "public_key": result["public_key"],
        "sign_count": result["sign_count"],
        "transports": result.get("transports"),
        "authenticator_type": result.get("authenticator_type")
    }

    db["webauthn_credentials"].insert_one(credential)

    db["students"].update_one(
        {"student_id": current_student["student_id"]},
        {"$set": {"biometric_registered": True}}
    )
    
    return {
        "message": "Fingerprint registered successfully",
        "status": "success"
    }


@router.post("/authenticate/options", response_model=WebAuthnAuthenticateOptions)
async def get_webauthn_authenticate_options(
    student_id: int,
):
    """Get WebAuthn authentication options"""
    
    db = get_database()

    # Verify student exists and has biometric registered
    student = db["students"].find_one({"student_id": student_id})
    if not student or not student.get("biometric_registered"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or biometric not registered"
        )
    
    options = WebAuthnService.generate_authentication_options(student_id)
    
    return WebAuthnAuthenticateOptions(**options)


@router.post("/authenticate/verify")
async def verify_webauthn_authentication(
    payload: dict,
):
    """Verify WebAuthn authentication response"""
    
    db = get_database()
    student_id = payload.get("student_id")
    response = payload.get("response")
    challenge = payload.get("challenge")
    if not student_id or not response or not challenge:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authentication payload")

    student = db["students"].find_one({"student_id": student_id})
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get credential
    credential = db["webauthn_credentials"].find_one({
        "credential_id": response.get("rawId")
    })

    if not credential or credential.get("student_id") != student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credential"
        )
    
    # Verify authentication
    challenge_bytes = base64.b64decode(challenge)
    
    new_sign_count = WebAuthnService.verify_authentication(
        credential_id=response.get("rawId", ""),
        client_data_json=response.get("response", {}).get("clientDataJSON", ""),
        authenticator_data=response.get("response", {}).get("authenticatorData", ""),
        signature=response.get("response", {}).get("signature", ""),
        challenge=challenge_bytes,
        stored_public_key=credential.get("public_key"),
        stored_sign_count=credential.get("sign_count", 0)
    )
    
    if new_sign_count is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed"
        )
    
    # Update sign count
    db["webauthn_credentials"].update_one(
        {"credential_id": credential["credential_id"]},
        {"$set": {"sign_count": new_sign_count}}
    )
    
    return {
        "message": "Authentication successful",
        "status": "success",
        "student_id": student_id
    }
