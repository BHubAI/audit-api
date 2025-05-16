from dataclasses import dataclass
from datetime import datetime, timezone

from opensearchpy import OpenSearch

from config.settings import settings
from core.repositories.search_engine_client import SearchEngineClient
from core.use_case.create_audit_use_case import UseCaseInput as CreateAuditInput


@dataclass
class OpenSearchClient(SearchEngineClient):
    client = OpenSearch(
        hosts=[{"host": settings.open_search_domain, "port": settings.opensearch_port}]
    )

    def upsert(self, data: CreateAuditInput) -> dict:
        now = datetime.now(timezone.utc)
        app_name = data.application.lower().replace("_", "-")
        index = f"audit-{app_name}-{now.strftime('%Y.%m')}"
        document = data.model_dump()

        response = self.client.index(index=index, body=document, refresh="true")

        return response
