#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"

usage() {
  cat <<USAGE
Usage:
  codex_data_runner.sh status
  codex_data_runner.sh info <dataset_id>
  codex_data_runner.sh validate <dataset_id>
  codex_data_runner.sh validate-mdx
  codex_data_runner.sh validate-charts
  codex_data_runner.sh validate-dataset <dataset_id>
USAGE
}

cmd="${1:-}"
case "$cmd" in
  status)
    cd "$TOOLS_DIR"
    python3 -m registry list
    ;;
  info)
    dataset_id="${2:-}"
    if [ -z "$dataset_id" ]; then
      echo "dataset_id is required" >&2
      exit 1
    fi
    cd "$TOOLS_DIR"
    python3 -m registry info "$dataset_id"
    ;;
  validate)
    dataset_id="${2:-}"
    if [ -z "$dataset_id" ]; then
      echo "dataset_id is required" >&2
      exit 1
    fi
    cd "$ROOT_DIR"
    python3 tools/scripts/validate_dataset.py --all "$dataset_id" --base-dir data/data.mn
    ;;
  validate-mdx)
    cd "$ROOT_DIR"
    python3 tools/scripts/validate_mdx_datafiles.py
    ;;
  validate-charts)
    cd "$ROOT_DIR/data.mn"
    python3 ../tools/scripts/validate_vega.py --all --data-root public
    ;;
  validate-dataset)
    dataset_id="${2:-}"
    if [ -z "$dataset_id" ]; then
      echo "dataset_id is required" >&2
      exit 1
    fi
    cd "$ROOT_DIR"
    python3 tools/tests/run_all_checks.py "$dataset_id"
    ;;
  *)
    usage
    exit 1
    ;;
esac
