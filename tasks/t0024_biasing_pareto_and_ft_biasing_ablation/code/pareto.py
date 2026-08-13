"""Pareto frontier computation over t0022's/t0023's existing biasing hyperparameter sweeps.

Part A of t0024 (see plan/plan.md ## Approach): pure local re-analysis, no new inference. Computes
the *true* non-dominated-point Pareto frontier (brand_exact_rate maximized, neutral_wer minimized)
for both the TDT and unified biasing sweeps, locates the live-prod TDT point relative to its
frontier, and selects one recommended production cell per model via an explicit, code-enforced
marginal-ratio stance.

Usage (local, no GPU needed):
    uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/pareto.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from tasks.t0024_biasing_pareto_and_ft_biasing_ablation.code import paths

EXPECTED_SWEEP_ROWS: int = 100
RATIO_THRESHOLD_DEFAULT: float = 1.0

TDT_MODEL_NAME: str = "parakeet-tdt-0.6b-v3"
UNIFIED_MODEL_NAME: str = "parakeet-unified-en-0.6b"

LIVE_PROD_CONTEXT_SCORE: float = 3.0
LIVE_PROD_DEPTH_SCALING: float = 0.5
LIVE_PROD_ALPHA: float = 1.5

TDT_SELECTION_STANCE: str = (
    "marginal delta_neutral_wer / delta_brand_exact_rate <= 1.0 against the last-accepted point, "
    "scanning the frontier ascending by neutral_wer, TDT baseline = current live-prod point"
)
UNIFIED_SELECTION_STANCE: str = (
    "marginal delta_neutral_wer / delta_brand_exact_rate <= 1.0 against the last-accepted point, "
    "scanning the frontier ascending by neutral_wer, unified baseline = the lowest-neutral_wer "
    "frontier cell (unified is not deployed, so there is no live-prod reference)"
)


@dataclass(frozen=True, slots=True)
class SweepRow:
    context_score: float
    depth_scaling: float
    alpha: float
    brand_exact_rate: float
    neutral_wer: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> SweepRow:
        return SweepRow(
            context_score=float(data["context_score"]),
            depth_scaling=float(data["depth_scaling"]),
            alpha=float(data["alpha"]),
            brand_exact_rate=float(data["brand_exact_rate"]),
            neutral_wer=float(data["neutral_wer"]),
        )


class ParetoCell(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    context_score: float
    depth_scaling: float
    alpha: float
    brand_exact_rate: float
    neutral_wer: float


class ParetoReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str
    source_file: str
    n_rows: int
    frontier: list[ParetoCell]
    live_prod_point: ParetoCell | None = None
    live_prod_on_frontier: bool | None = None
    live_prod_dominated_by: list[ParetoCell] | None = None
    selected_cell: ParetoCell
    selection_stance: str


def load_sweep(path: Path) -> list[SweepRow]:
    rows: list[SweepRow] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip() == "":
                continue
            rows.append(SweepRow.from_dict(json.loads(line)))
    return rows


def pareto_frontier(rows: list[SweepRow]) -> list[SweepRow]:
    """True non-dominated-point filter: not a "sort then keep increasing" scan.

    A row is on the frontier iff no other row has both neutral_wer <= its neutral_wer and
    brand_exact_rate >= its brand_exact_rate, with at least one strict inequality. The naive
    single-pass scan can retain a dominated point when two rows share the same neutral_wer, which
    both t0022's and t0023's sweeps do (see plan/plan.md ## Approach).
    """
    frontier: list[SweepRow] = []
    for row in rows:
        dominated = False
        for other in rows:
            if other is row:
                continue
            not_worse = (
                other.neutral_wer <= row.neutral_wer
                and other.brand_exact_rate >= row.brand_exact_rate
            )
            strictly_better = (
                other.neutral_wer < row.neutral_wer or other.brand_exact_rate > row.brand_exact_rate
            )
            if not_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(row)
    return sorted(frontier, key=lambda r: r.neutral_wer)


def select_frontier_cell(
    frontier: list[SweepRow],
    baseline: SweepRow,
    *,
    ratio_threshold: float = RATIO_THRESHOLD_DEFAULT,
) -> SweepRow:
    """Walk the frontier ascending by neutral_wer, accepting cheap brand_exact_rate gains.

    A candidate is accepted (becomes the new baseline) only if it gains brand_exact_rate over the
    current baseline (delta_brand > 0 — a candidate that does not gain brand_exact_rate is never a
    valid purchase, regardless of its wer) and the marginal ratio delta_neutral_wer / delta_brand,
    measured against the current accepted point, is <= ratio_threshold. The scan continues through
    the whole frontier regardless of a rejection (a later candidate is still compared against the
    last-accepted point, not the immediately-preceding frontier row).
    """
    accepted = baseline
    for candidate in frontier:
        delta_brand = candidate.brand_exact_rate - accepted.brand_exact_rate
        if delta_brand <= 0:
            continue
        delta_wer = candidate.neutral_wer - accepted.neutral_wer
        ratio = delta_wer / delta_brand
        if ratio <= ratio_threshold:
            accepted = candidate
    return accepted


def find_row(
    rows: list[SweepRow],
    *,
    context_score: float,
    depth_scaling: float,
    alpha: float,
) -> SweepRow:
    matches = [
        r
        for r in rows
        if r.context_score == context_score
        and r.depth_scaling == depth_scaling
        and r.alpha == alpha
    ]
    assert len(matches) == 1, (
        f"exactly one row exists for cs={context_score}/ds={depth_scaling}/alpha={alpha}"
    )
    return matches[0]


def dominators(rows: list[SweepRow], target: SweepRow) -> list[SweepRow]:
    return [
        r
        for r in rows
        if r != target
        and r.neutral_wer <= target.neutral_wer
        and r.brand_exact_rate >= target.brand_exact_rate
    ]


def _to_cell(row: SweepRow) -> ParetoCell:
    return ParetoCell(
        context_score=row.context_score,
        depth_scaling=row.depth_scaling,
        alpha=row.alpha,
        brand_exact_rate=row.brand_exact_rate,
        neutral_wer=row.neutral_wer,
    )


def main() -> None:
    unified_rows = load_sweep(paths.T0022_SWEEP)
    tdt_rows = load_sweep(paths.T0023_SWEEP)
    assert len(unified_rows) == EXPECTED_SWEEP_ROWS, (
        f"t0022 param_sweep.jsonl has {EXPECTED_SWEEP_ROWS} rows"
    )
    assert len(tdt_rows) == EXPECTED_SWEEP_ROWS, (
        f"t0023 tdt_sweep.jsonl has {EXPECTED_SWEEP_ROWS} rows"
    )

    tdt_frontier = pareto_frontier(tdt_rows)
    unified_frontier = pareto_frontier(unified_rows)
    assert len(unified_frontier) > 0, "unified frontier is non-empty"

    live_prod = find_row(
        tdt_rows,
        context_score=LIVE_PROD_CONTEXT_SCORE,
        depth_scaling=LIVE_PROD_DEPTH_SCALING,
        alpha=LIVE_PROD_ALPHA,
    )
    live_prod_on_frontier = live_prod in tdt_frontier
    live_prod_dominators = [] if live_prod_on_frontier else dominators(tdt_rows, live_prod)

    tdt_selected = select_frontier_cell(tdt_frontier, live_prod)
    unified_selected = select_frontier_cell(unified_frontier, unified_frontier[0])

    tdt_report = ParetoReport(
        model=TDT_MODEL_NAME,
        source_file="tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl",
        n_rows=len(tdt_rows),
        frontier=[_to_cell(r) for r in tdt_frontier],
        live_prod_point=_to_cell(live_prod),
        live_prod_on_frontier=live_prod_on_frontier,
        live_prod_dominated_by=[_to_cell(r) for r in live_prod_dominators],
        selected_cell=_to_cell(tdt_selected),
        selection_stance=TDT_SELECTION_STANCE,
    )
    unified_report = ParetoReport(
        model=UNIFIED_MODEL_NAME,
        source_file="tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl",
        n_rows=len(unified_rows),
        frontier=[_to_cell(r) for r in unified_frontier],
        selected_cell=_to_cell(unified_selected),
        selection_stance=UNIFIED_SELECTION_STANCE,
    )

    paths.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (paths.RESULTS_DIR / "pareto_tdt.json").write_text(
        tdt_report.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (paths.RESULTS_DIR / "pareto_unified.json").write_text(
        unified_report.model_dump_json(indent=2, exclude_none=True) + "\n", encoding="utf-8"
    )

    print(f"TDT frontier: {len(tdt_frontier)} cells; live_prod_on_frontier={live_prod_on_frontier}")
    print(f"TDT selected cell: {tdt_selected}")
    print(f"Unified frontier: {len(unified_frontier)} cells")
    print(f"Unified selected cell: {unified_selected}")


if __name__ == "__main__":
    main()
