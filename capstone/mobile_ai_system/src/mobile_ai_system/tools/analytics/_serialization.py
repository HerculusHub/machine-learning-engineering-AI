"""
Analytics Tool Serialization Helpers

Step 11C
--------

Purpose
-------
Convert runtime analytics dataclass results into plain
Python dictionaries suitable for:

- Analysis Agent state
- tool outputs
- JSON serialization
- Evaluation Agent inspection

This module contains no analytical logic.
"""

from __future__ import annotations

from dataclasses import (
    asdict,
    is_dataclass,
)

from typing import Any

import numpy as np


def analytics_result_to_dict(
    value: Any,
) -> Any:
    """
    Recursively convert analytics results into JSON-friendly
    Python structures.

    Supported values
    ----------------
    - dataclasses
    - dictionaries
    - lists
    - tuples
    - NumPy scalar values
    - ordinary Python values
    """

    if is_dataclass(
        value
    ):

        return analytics_result_to_dict(
            asdict(
                value
            )
        )

    if isinstance(
        value,
        dict,
    ):

        return {
            str(
                key
            ): analytics_result_to_dict(
                item
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):

        return [
            analytics_result_to_dict(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        np.integer,
    ):

        return int(
            value
        )

    if isinstance(
        value,
        np.floating,
    ):

        return float(
            value
        )

    if isinstance(
        value,
        np.bool_,
    ):

        return bool(
            value
        )

    return value

