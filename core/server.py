import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from strawberry.fastapi import GraphQLRouter
from api.v1.common import schema
from sqlalchemy.ext.asyncio import AsyncSession
# from app.controllers.company import CompanyController
# from api import router
# from core.config import config
from core.database.db import init_db
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    # AuthBackend,
    AuthenticationMiddleware,
    ResponseLoggerMiddleware,
    SQLAlchemyMiddleware,
)
from core.database.session import get_db
import os 
def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


# def init_routers(app_: FastAPI) -> None:
#     app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

origins = [
    "http://192.168.9.230:3000/",  # React frontend (adjust port as needed)
]

def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        # Middleware(
        #     AuthenticationMiddleware,
        #     backend=AuthBackend(),
        #     on_error=on_auth_error,
        # ),
        Middleware(SQLAlchemyMiddleware),
        Middleware(ResponseLoggerMiddleware),
    ]
    return middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    # You can initialize connections, services here
    yield
    print("Shutting down...")
    # Close connections, services here
    await asyncio.sleep(1)  # Example cleanup (like closing DB connections)
    
def create_app() -> FastAPI:
    app_ = FastAPI(
        title="e-commerce",
        description="e-commerce",
        version="1.0.0",
        docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
        redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
        lifespan=lifespan
    )
    # init_routers(app_=app_)
    init_listeners(app_=app_)
    return app_

# async def get_context(db: AsyncSession = Depends(get_db)):
#     return {
#         "db": db,
#         "company_controller": CompanyController()
#     }
from core.database.db import SessionLocal

async def get_context(request: Request):
    # Extract the authorization header from the request
    authorization_header = request.headers.get('authorization')

    # Create the context with db and authorization header
    async with SessionLocal() as session:
        return {
            "db": session,
            "authorization": authorization_header  # Add the authorization header here
        }
        
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app = create_app()
app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def startup():
    await init_db()
    
# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    custom_errors = []
    
    for error in errors:
        field = error.get('loc')[-1]  # Get the field name
        error_msg = error.get('msg')  # Get the error message
        custom_errors = f"{field} : {error_msg}"

        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": custom_errors,
                "status": "error",
                "data": []
            },
        )
