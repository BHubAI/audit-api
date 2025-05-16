from dependency_injector import containers

from core.use_case.create_audit_use_case import CreateAuditUseCase


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container.
    Manages the lifecycle of the application objects and their dependencies.
    Automates the process of creating an configuring objects by injecting
    them with their required dependencies throughout the app code.
    """

    wiring_config = containers.WiringConfiguration(
        packages=[
            "presentation.api.v1.routes",
        ]
    )

    create_audit_use_case = containers.Factory(CreateAuditUseCase)
