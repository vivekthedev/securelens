from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field
from typing_extensions import TypeAlias


class Success(BaseModel):
    """Response when SQL could be successfully generated."""

    sql_query: str
    explanation: str = Field(
        "", description="Explanation of the SQL query, as markdown"
    )


class InvalidInformation(BaseModel):
    """Response the user input didn't include enough information to generate SQL."""

    error_message: str


SQLResponse: TypeAlias = Union[Success, InvalidInformation]


class PermissionSchema(BaseModel):
    """Schema for permission check"""

    action: str
    resource: str


class InvalidRequest(BaseModel):
    """Schema for invalid request"""

    message: str


ExtractResponse: TypeAlias = Union[PermissionSchema, InvalidRequest]


class CheckResponse(BaseModel):
    """Schema for check response. if the user is allowed to proceed or not"""

    can_proceed: bool
    message: str = Field("", description="Message to be displayed to the user")
