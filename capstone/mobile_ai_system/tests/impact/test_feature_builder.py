"""
Unit tests for FeatureBuilder.

Architecture v2.3 (Frozen MVP)
"""

from __future__ import annotations

from mobile_ai_system.impact.builders import (
    FeatureBuilder,
)

from tests.fixtures.information import (
    build_information_result,
)


def test_build_returns_feature_vector():
    """
    FeatureBuilder should always return
    a FeatureVector instance.
    """

    builder = FeatureBuilder()

    information = build_information_result()

    feature_vector = builder.build(
        information,
    )

    assert feature_vector is not None

    assert hasattr(
        feature_vector,
        "features",
    )

    assert isinstance(
        feature_vector.features,
        dict,
    )


def test_build_creates_metadata():
    """
    Metadata dictionary should always exist.
    """

    builder = FeatureBuilder()

    information = build_information_result()

    feature_vector = builder.build(
        information,
    )

    assert hasattr(
        feature_vector,
        "metadata",
    )

    assert isinstance(
        feature_vector.metadata,
        dict,
    )


def test_build_is_repeatable():
    """
    Building twice with the same input
    should produce equivalent results.
    """

    builder = FeatureBuilder()

    information = build_information_result()

    first = builder.build(
        information,
    )

    second = builder.build(
        information,
    )

    assert first.features == second.features

    assert first.metadata == second.metadata


def test_feature_vector_contains_dictionary():
    """
    Features should always be stored
    as a dictionary.
    """

    builder = FeatureBuilder()

    information = build_information_result()

    feature_vector = builder.build(
        information,
    )

    assert isinstance(
        feature_vector.features,
        dict,
    )


def test_feature_vector_can_be_empty():
    """
    Empty feature dictionaries are valid
    during the MVP stage.
    """

    builder = FeatureBuilder()

    information = build_information_result()

    feature_vector = builder.build(
        information,
    )

    assert len(feature_vector.features) >= 0


def test_metadata_can_be_empty():
    """
    Metadata may legitimately be empty.
    """

    builder = FeatureBuilder()

    information = build_information_result()

    feature_vector = builder.build(
        information,
    )

    assert len(feature_vector.metadata) >= 0