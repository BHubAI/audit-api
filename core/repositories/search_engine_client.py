from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.use_case.create_audit_use_case import UseCaseInput as CreateAuditInput


@dataclass
class SearchEngineClient(ABC):
    @abstractmethod
    def upsert(self, data: CreateAuditInput) -> dict:
        pass
