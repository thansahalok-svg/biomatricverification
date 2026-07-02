import base64
from typing import Optional, List, Dict, Any
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    UserVerificationRequirement,
    AuthenticatorSelectionCriteria,
    AttestationConveyancePreference,
    ResidentKeyRequirement,
    AuthenticatorAttachment,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from app.config import settings


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


class WebAuthnService:
    """Service for WebAuthn registration and authentication"""
    
    @staticmethod
    def generate_registration_options(
        user_id: int,
        username: str,
        user_display_name: str
    ) -> Dict[str, Any]:
        """Generate WebAuthn registration options"""
        
        registration_options = generate_registration_options(
            rp_id=settings.RP_ID,
            rp_name=settings.RP_NAME,
            user_id=str(user_id),
            user_name=username,
            user_display_name=user_display_name,
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
            attestation=AttestationConveyancePreference.DIRECT,
        )
        
        return {
            "challenge": base64.b64encode(registration_options.challenge).decode("utf-8"),
            "rp": registration_options.rp.__dict__,
            "user": {
                "id": base64.b64encode(registration_options.user.id).decode("utf-8"),
                "name": registration_options.user.name,
                "displayName": registration_options.user.display_name,
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": alg}
                for alg in [-7, -257]
            ],
            "timeout": registration_options.timeout,
            "attestation": registration_options.attestation.value,
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "residentKey": "preferred",
                "userVerification": "preferred",
            },
        }
    
    @staticmethod
    def generate_authentication_options(user_id: int) -> Dict[str, Any]:
        """Generate WebAuthn authentication options"""
        
        auth_options = generate_authentication_options(
            rp_id=settings.RP_ID,
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        
        return {
            "challenge": base64.b64encode(auth_options.challenge).decode("utf-8"),
            "timeout": auth_options.timeout,
            "rpId": settings.RP_ID,
            "userVerification": "preferred",
            "allowCredentials": None,
        }
    
    @staticmethod
    def verify_registration(
        credential_id: str,
        client_data_json: str,
        attestation_object: str,
        challenge: bytes
    ) -> Optional[Dict[str, Any]]:
        """Verify WebAuthn registration response"""
        try:
            credential = {
                "id": credential_id,
                "rawId": credential_id,
                "type": "public-key",
                "response": {
                    "clientDataJSON": client_data_json,
                    "attestationObject": attestation_object,
                },
            }

            verified_registration = verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=settings.RP_ID,
                expected_origin=settings.ORIGIN,
                require_user_verification=False,
            )

            return {
                "credential_id": base64url_encode(verified_registration.credential_id),
                "public_key": verified_registration.credential_public_key,
                "sign_count": verified_registration.sign_count,
                "transports": None,
                "authenticator_type": str(verified_registration.credential_device_type),
            }
        except Exception as e:
            print(f"Registration verification failed: {str(e)}")
            return None
    
    @staticmethod
    def verify_authentication(
        credential_id: str,
        client_data_json: str,
        authenticator_data: str,
        signature: str,
        challenge: bytes,
        stored_public_key: bytes,
        stored_sign_count: int
    ) -> Optional[int]:
        """Verify WebAuthn authentication response and return new sign count"""
        try:
            credential = {
                "id": credential_id,
                "rawId": credential_id,
                "type": "public-key",
                "response": {
                    "clientDataJSON": client_data_json,
                    "authenticatorData": authenticator_data,
                    "signature": signature,
                },
            }

            verified_auth = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=settings.RP_ID,
                expected_origin=settings.ORIGIN,
                credential_public_key=stored_public_key,
                credential_current_sign_count=stored_sign_count,
                require_user_verification=False,
            )

            return verified_auth.new_sign_count
        except Exception as e:
            print(f"Authentication verification failed: {str(e)}")
            return None
