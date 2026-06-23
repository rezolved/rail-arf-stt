"""Wrapper script to regenerate data/analysis_output.json.

This is a thin wrapper around compute_metrics.main() for use with run_with_logs.
"""

from tasks.t0002_baseline_evaluation.code.compute_metrics import main

if __name__ == "__main__":
    main()
