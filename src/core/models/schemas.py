"""Pydantic schemas for API request/response validation"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class MindmapGenerationRequest(BaseModel):
    """Request schema for mindmap generation"""

    document: str = Field(
        ...,
        description="Text document to generate mindmap from",
        min_length=10
    )
    lang: Optional[str] = Field(
        default=None,
        description="Language code (en, ar). If not provided, will be auto-detected"
    )
    max_depth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum depth of hierarchical clustering"
    )
    min_size: int = Field(
        default=2,
        ge=1,
        le=100,
        description="Minimum cluster size"
    )

    @field_validator('document')
    @classmethod
    def validate_document(cls, v):
        if not v or not v.strip():
            raise ValueError("Document cannot be empty")
        return v.strip()

    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v):
        if v and v not in ['en', 'ar', 'English', 'Arabic', None]:
            raise ValueError("Language must be 'en', 'ar', 'English', or 'Arabic'")
        return v


class MindmapNodeSchema(BaseModel):
    """Schema for a mindmap node"""

    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node display label")
    children: List['MindmapNodeSchema'] = Field(
        default_factory=list,
        description="Child nodes"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional detailed description"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata"
    )


# Enable self-referencing for recursive model
MindmapNodeSchema.model_rebuild()


class MindmapResponse(BaseModel):
    """Response schema for mindmap generation"""

    success: bool = Field(..., description="Operation success status")
    mindmap: MindmapNodeSchema = Field(..., description="Generated mindmap tree")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata"
    )


class FilePreprocessResponse(BaseModel):
    """Response schema for file preprocessing"""

    success: bool = Field(..., description="Operation success status")
    filename: str = Field(..., description="Original filename")
    processed_text: str = Field(..., description="Extracted and processed text")
    text_length: int = Field(..., description="Length of processed text")
    detected_language: Optional[str] = Field(
        default=None,
        description="Auto-detected language"
    )


class HealthCheckResponse(BaseModel):
    """Response schema for health check"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual services"
    )


class ErrorResponse(BaseModel):
    """Error response schema"""

    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
