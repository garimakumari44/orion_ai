"""
Tests for knowledge system validator models.

Covers:

- Pydantic model availability
- object creation
- default values
- validation behavior
"""

from uuid import uuid4

import pytest


from app.knowledge_system.validators import (
    document,
    embedding,
    entity,
    metadata,
    relationship,
    quality,
)



# ---------------------------------------------------------
# Embedding Models
# ---------------------------------------------------------


def test_embedding_model_creation():

    obj = embedding.EmbeddingModel(
        document_id=uuid4(),
        chunk_id=uuid4(),
        vector=[0.1, 0.2, 0.3],
        dimension=3,
        provider="openai",
        model_name="text-embedding"
    )

    assert obj.dimension == 3
    assert len(obj.vector) == 3



def test_embedding_request_validation():

    obj = embedding.EmbeddingRequest(
        text="hello world",
        provider="openai",
        model_name="embedding-model"
    )

    assert obj.text == "hello world"



def test_embedding_response_creation():

    obj = embedding.EmbeddingResponse(
        vector=[0.1],
        dimension=1,
        provider="openai",
        model_name="test"
    )

    assert obj.dimension == 1



# ---------------------------------------------------------
# Relationship Models
# ---------------------------------------------------------


def test_relationship_creation():

    obj = relationship.Relationship(
        source_id=uuid4(),
        target_id=uuid4(),
        relationship=relationship.RelationshipType.RELATED_TO
    )

    assert obj.confidence == 1.0
    assert obj.weight == 1.0



def test_relationship_enum_values():

    assert (
        relationship.RelationshipType.RELATED_TO.value
        == "related_to"
    )



# ---------------------------------------------------------
# Quality Models
# ---------------------------------------------------------


def test_quality_score_creation():

    obj = quality.QualityScore(
        resource_id=uuid4()
    )

    assert obj.overall_score == 1.0
    assert obj.completeness == 1.0



def test_quality_report_creation():

    obj = quality.QualityReport(
        resource_id=uuid4(),
        passed=True,
        message="Quality passed",
        score=0.95
    )

    assert obj.passed is True
    assert obj.score == 0.95



# ---------------------------------------------------------
# Module imports
# ---------------------------------------------------------


def test_all_validator_modules_import():

    assert document is not None
    assert embedding is not None
    assert entity is not None
    assert metadata is not None
    assert relationship is not None
    assert quality is not None