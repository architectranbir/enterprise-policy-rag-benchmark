from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request

from policy_rag.answering import PolicyAnswerService
from policy_rag.api.models import AskRequest, AskResponse, HealthResponse
from policy_rag.auth import (
    AuthenticatedIdentity,
    EntraTokenValidator,
    TokenValidationError,
    TokenValidator,
    bearer_token,
)
from policy_rag.domain.access import PolicyAccessContext
from policy_rag.retrieval.base import PolicyVectorStore
from policy_rag.retrieval.models import PolicyRetrievalRequest

if TYPE_CHECKING:
    from policy_rag.config import Settings


def create_app(
    service: PolicyAnswerService | None = None,
    store: PolicyVectorStore | None = None,
    token_validator: TokenValidator | None = None,
    close_runtime: Callable[[], None] | None = None,
    *,
    allow_insecure_demo_identity: bool = False,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        if close_runtime is not None:
            close_runtime()

    app = FastAPI(
        title="Enterprise Policy Intelligence API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.answer_service = service
    app.state.vector_store = store

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        backend = store.backend_name if store else "unconfigured"
        return HealthResponse(status="ok", backend=backend)

    @app.get("/ready", response_model=HealthResponse)
    def ready() -> HealthResponse:
        if store is None or not store.ready():
            raise HTTPException(status_code=503, detail="retrieval backend is not ready")
        return HealthResponse(status="ready", backend=store.backend_name)

    @app.post("/ask", response_model=AskResponse)
    def ask(
        payload: AskRequest,
        request: Request,
        x_correlation_id: str | None = Header(default=None),
        authorization: str | None = Header(default=None),
        x_demo_user_id: str | None = Header(default=None),
        x_demo_user_groups: str | None = Header(default=None),
    ) -> AskResponse:
        active_service: PolicyAnswerService | None = request.app.state.answer_service
        if active_service is None:
            raise HTTPException(status_code=503, detail="answer service is not configured")
        correlation_id = x_correlation_id or str(uuid4())
        try:
            if allow_insecure_demo_identity:
                groups = tuple(
                    group.strip()
                    for group in (x_demo_user_groups or "").split(",")
                    if group.strip()
                )
                identity = AuthenticatedIdentity(
                    user_id=x_demo_user_id or "",
                    user_groups=groups,
                )
            else:
                if token_validator is None:
                    raise TokenValidationError("token validator is not configured")
                identity = token_validator.validate(bearer_token(authorization))
        except (TokenValidationError, ValueError) as error:
            raise HTTPException(status_code=401, detail=str(error)) from error
        retrieval = PolicyRetrievalRequest(
            access=PolicyAccessContext(
                user_id=identity.user_id,
                user_groups=identity.user_groups,
                as_of=payload.as_of,
            ),
            document_id=payload.document_id,
            department=payload.department,
            classification=payload.classification,
            limit=payload.top_k,
        )
        result = active_service.ask(payload.question, retrieval)
        return AskResponse(**result.model_dump(), correlation_id=correlation_id)

    return app


def create_configured_app(settings: "Settings | None" = None) -> FastAPI:
    from policy_rag.config import Settings
    from policy_rag.runtime import build_runtime

    settings = settings or Settings()
    runtime = build_runtime(settings)
    validator = None
    if not settings.allow_insecure_demo_identity:
        validator = EntraTokenValidator(
            tenant_id=settings.entra_tenant_id,
            audience=settings.entra_audience,
            required_scope=settings.entra_required_scope,
            group_mapping=settings.entra_group_mapping,
        )
    return create_app(
        runtime.service,
        runtime.store,
        validator,
        runtime.close,
        allow_insecure_demo_identity=settings.allow_insecure_demo_identity,
    )


app = create_app()
