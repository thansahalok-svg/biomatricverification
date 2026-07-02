from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class WebAuthnRegisterOptions(BaseModel):
    """WebAuthn registration options to send to frontend"""
    challenge: str
    rp: dict
    user: dict
    pubKeyCredParams: List[dict]
    timeout: int
    attestation: str
    authenticatorSelection: dict


class WebAuthnRegisterResponse(BaseModel):
    """WebAuthn registration response from frontend"""
    id: str
    rawId: str
    response: dict
    type: str


class WebAuthnAuthenticateOptions(BaseModel):
    """WebAuthn authentication options"""
    challenge: str
    timeout: int
    rpId: str
    allowCredentials: Optional[List[dict]] = None
    userVerification: str


class WebAuthnAuthenticateResponse(BaseModel):
    """WebAuthn authentication response from frontend"""
    id: str
    rawId: str
    response: dict
    type: str
