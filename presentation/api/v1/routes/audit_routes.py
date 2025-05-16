from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from core.use_case.create_audit_use_case import CreateAuditUseCase
from core.use_case.create_audit_use_case import UseCaseInput as CreateAuditInput
from presentation.api.v1.dtos.audit_dtos import CreateAuditRequest, CreateAuditResponse
from presentation.di_container import Container

# audit_router = APIRouter(prefix="/v1/audit", dependencies=[Depends(JwtValidator())])
audit_router = APIRouter(
    prefix="/v1/audit",
)


@audit_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_audit(
    payload: CreateAuditRequest,
    use_case: CreateAuditUseCase = Depends(Provide[Container.create_audit_use_case]),
) -> CreateAuditResponse:
    """
    Create a audit data.

    Parameters:
    -----------
        payload (CreateAuditRequest): The request body.

    Returns:
    --------
        201 CREATED.
    """
    uc_input = CreateAuditInput(**payload.model_dump())
    use_case.execute(uc_input=uc_input)

    return CreateAuditResponse()
