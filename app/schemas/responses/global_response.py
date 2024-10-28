from pydantic import BaseModel
from typing import Any
from fastapi.responses import JSONResponse
from fastapi import status


class GlobalResponse(BaseModel):
    data: Any = []
    message: str = "Successfully fetched."

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        response_content = {
            "status": "Success",
            "data": instance.data,
            "message": "Successfully created",
        }
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_content)
    
    @classmethod
    def update(cls, **kwargs):
        instance = cls(**kwargs)
        response_content = {
            "status": "Success",
            "data": instance.data,
            "message": "Successfully updated.",
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=response_content)
    
    @classmethod
    def get(cls, **kwargs):
        instance = cls(**kwargs)
        response_content = {
            "status": "Success",
            "data": instance.data,
            "message": "Successfully fetched.",
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=response_content)

    @classmethod
    def delete(cls, **kwargs):
        instance = cls(**kwargs)
        response_content = {
            "status": "Success",
            "data": instance.data,
            "message": "Successfully deleted.",
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=response_content)
    

    @classmethod
    def exception(cls, **kwargs):
        response_content = {
            "status": "Error",
            "data": [],
            "message": "Something went wrong.",
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_content)
    

    @classmethod
    def bad_request(cls, **kwargs):
        instance = cls(**kwargs)
        response_content = {
            "status": "Error",
            "data": [],
            "message": instance.message,
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response_content)
    
    @classmethod
    def success(cls, **kwargs):
        instance = cls(**kwargs)
        response_content = {
            "status": "Success",
            "data": [],
            "message": instance.message,
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response_content)
    








