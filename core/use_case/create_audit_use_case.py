from dataclasses import dataclass
from typing import TypeAlias

from pydantic import BaseModel

from core.repositories.search_engine_client import SearchEngineClient
from core.use_case.base_use_case import BaseUseCase


class UseCaseInput(BaseModel):
    """
    Input for the use case.
    """

    actor: str
    event_type: str
    application: str
    cnpj: str
    resource_id: str
    timestamp: str
    metadata: dict


UseCaseOutput: TypeAlias = None


@dataclass
class CreateAuditUseCase(BaseUseCase):
    """
    Use case for creating an audit.
    """

    search_engine_client: SearchEngineClient

    def execute(self, uc_input: UseCaseInput) -> UseCaseOutput:
        """
        Execute the use case.

        :param audit: The audit to create.
        :return: The created audit.
        """
        self.search_engine_client.upsert(
            data=uc_input,
        )
