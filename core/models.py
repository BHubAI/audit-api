from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class DomainBaseModel(BaseModel):
    """
    Base domain model. Holds the common attributes among all domain models

    Attributes
    ----------
    id : str
        The object's universal unique identifier (UUID)
    created_at : Optional[datetime]
        The date and time of the object creation
    """

    id: str = Field(
        description="Object's universal unique identifier.",
        default_factory=lambda: str(uuid4()),
    )
    created_at: Optional[datetime] = Field(
        description="Date and time of object's creation.",
        default_factory=lambda: datetime.now(timezone.utc),
    )


class SampleChildModel(DomainBaseModel):
    """
    Represents a Sample Child

    Attributes
    ----------
    sample_id : str
        The id of the Sample associated to this child.
    """

    sample_id: str = Field(description="Id of the child associated to the file.")


class SampleModel(DomainBaseModel):
    """
    Represents the Sample Model

    Attributes
    ----------
    title : str
        The title of the Sample.
    """

    title: str = Field(description="Title of the sample.")

    children: Optional[list[SampleChildModel]] = Field(
        description="list of children of the Sample", default=[]
    )
