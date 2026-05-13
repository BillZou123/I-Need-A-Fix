import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"



if settings.SENTRY_DSN and settings.ENVIRONMENT != "local": 
    # sentry is a platform for error tracking and monitoring. It helps developers identify and fix issues in their applications by providing real-time error tracking and performance monitoring. By initializing Sentry with the DSN (Data Source Name) and enabling tracing, developers can capture and analyze errors and performance data to improve the overall quality of their application.
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # this is the URL where the OpenAPI schema will be available. It is constructed by combining the API version string (settings.API_V1_STR) with the path "/openapi.json". This allows clients to access the OpenAPI schema for the API, which describes the available endpoints, request/response formats, and other details about the API.
    generate_unique_id_function=custom_generate_unique_id, #this is a custom function that generates unique IDs for API routes(endpoints). It takes an APIRoute object as input and returns a string that combines the first tag of the route and the route name. This can be useful for organizing and identifying routes in the API documentation or for other purposes where unique identifiers are needed.
)

# Set all CORS enabled origins
# Frontend request
#     ↓
# CORS middleware checks if origin is allowed
#     ↓
# FastAPI route handles the request
#     ↓
# Response goes back through CORS middleware
#     ↓
# Browser receives the response if CORS checks pass, otherwise it blocks the response due to CORS
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins, #Allow frontend origins like: http://localhost:5173
        allow_credentials=True, #Allow cookies/auth credentials
        allow_methods=["*"], #Allow all HTTP methods
        allow_headers=["*"], #Allow all headers
    )

app.include_router(api_router, prefix=settings.API_V1_STR) #Add all routes inside api_router to the real FastAPI app, with the prefix defined in settings.API_V1_STR (e.g., "/api/v1"). 
#This means that all endpoints defined in api_router will be accessible under the specified prefix, helping to organize the API versioning and structure.
