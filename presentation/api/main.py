import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from presentation.api.exception_handlers import inject_exception_handlers
from presentation.api.v1.routes.audit_routes import samples_router
from presentation.di_container import Container


class Main:
    """Bootstraps the application"""

    app: FastAPI = FastAPI()
    container: Container = Container()

    @classmethod
    def create_app(cls) -> FastAPI:
        """Defines the application setup"""
        cls.app.include_router(samples_router)

        cls.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        inject_exception_handlers(cls.app)

        return cls.app


logging.basicConfig(level=logging.INFO)

app = Main.create_app()
