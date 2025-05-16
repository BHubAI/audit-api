from pydantic import BaseModel


class CreateAuditRequest(BaseModel):
    """Parses the payload of the Create audit Request"""

    actor: str
    event_type: str
    application: str
    cnpj: str
    resource_id: str
    timestamp: str
    metadata: dict


class CreateAuditResponse(BaseModel):
    """Parses the payload of the Create audit Response"""
