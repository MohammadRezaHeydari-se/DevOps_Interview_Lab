"""Category weighting for interview building.

Pure, stateless math: combine role profile areas with an optional company
focus, and allocate a question quota across categories proportionally to their
weights. Kept separate from session building so weighting can be reasoned about
and tested on its own.
"""

from __future__ import annotations

from typing import Dict, Mapping, Optional


def combine_weights(
    role_areas: Mapping[str, float],
    company_focus: Optional[Mapping[str, float]] = None,
) -> Dict[str, float]:
    """Combine role area weights with an optional company focus.

    Role areas always define the categories and the base weights. A company
    focus only adjusts the weight of categories the role already defines; it
    never adds or replaces areas. A category the role defines but the company
    does not mention keeps its full role weight.
    """
    weights = {area: float(weight) for area, weight in role_areas.items()}
    if company_focus is None:
        return weights
    return {
        area: weight * float(company_focus.get(area, 1.0))
        for area, weight in weights.items()
    }


def allocate_quota(weights: Mapping[str, float], total: int) -> Dict[str, int]:
    """Distribute `total` slots across categories proportionally to weights.

    Uses the largest-remainder method, so the counts are deterministic and sum
    to `total` when enough positive weights exist. Ties are broken by category
    name so the result does not depend on mapping order.
    """
    if total <= 0:
        return {}
    positive = {area: float(weight) for area, weight in weights.items() if weight > 0}
    if not positive:
        return {}
    weight_sum = sum(positive.values())
    quotas = {area: total * weight / weight_sum for area, weight in positive.items()}
    counts = {area: int(quota) for area, quota in quotas.items()}
    remainder = total - sum(counts.values())
    if remainder > 0:
        ordered = sorted(
            positive,
            key=lambda area: (-(quotas[area] - counts[area]), area),
        )
        for area in ordered[:remainder]:
            counts[area] += 1
    return counts
