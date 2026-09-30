#!/usr/bin/env python3
"""
Put a dataset's EN and MN CSVs in the same row order.

Long-format bilingual CSVs (category, date, value) must be row-aligned: row i
of the MN file is the translation of row i of the EN file. Sorting each file
by its own category labels breaks that ("Bread" sorts before "Flour", but
"Гурил" sorts before "Талх"), and run_all_checks.py then fails its EN/MN
numeric comparisons.

Files whose rows already correspond are left as they are, in whatever order.
Otherwise this sorts the EN file by (category, date) and reorders the MN file
to match.
EN and MN categories are paired by their full value series (every date and
value must match), so no translation table is needed. The pairing must be
one-to-one; ambiguous or unmatched categories abort without writing.

Two-column snapshots (category, value), e.g. `*-latest` map files, have one
value per category, too little to pair on; they take the pairing from a
long-format sibling (`--pairs-from`, default: the id with `-latest` replaced
by `-all`) and keep the EN row order.

Usage:
    python3 tools/scripts/align_bilingual_rows.py weekly-bread-prices-ulaanbaatar
    python3 tools/scripts/align_bilingual_rows.py --check weekly-*   # report only
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

DATASETS = Path(__file__).resolve().parents[2] / "data.mn/public/datasets"


def roles(df: pd.DataFrame):
    """(category, date, value) column names for a 3-column long CSV."""
    if df.shape[1] != 3:
        raise ValueError(f"expected 3 columns (category, date, value), got {list(df.columns)}")
    value = next(c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]))
    date = next(c for c in df.columns if c != value and df[c].astype(str).str.match(r"^\d{4}-\d{2}").all())
    category = next(c for c in df.columns if c not in (value, date))
    return category, date, value


def series_key(df, category, date, value, label):
    part = df[df[category] == label].sort_values(date)
    return tuple(zip(part[date].astype(str), part[value].round(6)))


def load(dataset_id: str):
    en_path, mn_path = DATASETS / f"{dataset_id}-en.csv", DATASETS / f"{dataset_id}-mn.csv"
    en, mn = pd.read_csv(en_path), pd.read_csv(mn_path)
    if len(en) != len(mn):
        raise ValueError(f"{dataset_id}: EN has {len(en)} rows, MN has {len(mn)}")
    return en_path, mn_path, en, mn


def category_pairing(dataset_id: str) -> dict:
    """EN -> MN category labels of a long-format dataset, by value series."""
    _, _, en, mn = load(dataset_id)
    (ec, ed, ev), (mc, md, mv) = roles(en), roles(mn)
    mn_by_series = {}
    for label in mn[mc].unique():
        mn_by_series.setdefault(series_key(mn, mc, md, mv, label), []).append(label)
    pairing = {}
    for label in en[ec].unique():
        match = mn_by_series.get(series_key(en, ec, ed, ev, label), [])
        if len(match) != 1:
            raise ValueError(f"{dataset_id}: EN '{label}' matches {len(match)} MN series {match}")
        pairing[label] = match[0]
    if len(set(pairing.values())) != len(pairing):
        raise ValueError(f"{dataset_id}: EN/MN category pairing is not one-to-one")
    return pairing


def align_snapshot(dataset_id: str, pairs_from: str, write: bool) -> bool:
    en_path, mn_path, en, mn = load(dataset_id)
    (ec, ev), (mc, mv) = en.columns, mn.columns
    pairing = category_pairing(pairs_from)
    missing = set(en[ec]) - set(pairing)
    if missing:
        raise ValueError(f"{dataset_id}: no pairing in {pairs_from} for {sorted(missing)}")
    mn_sorted = pd.DataFrame({mc: en[ec].map(pairing)}).merge(
        mn, on=mc, how="left", validate="one_to_one")[list(mn.columns)]
    if not (mn_sorted[mv].values == en[ev].values).all():
        raise ValueError(f"{dataset_id}: values differ after pairing via {pairs_from}")
    aligned = mn.equals(mn_sorted)
    if write and not aligned:
        mn_sorted.to_csv(mn_path, index=False)
    print(f"{'aligned' if aligned else ('REORDERED' if write else 'MISALIGNED'):10} {dataset_id} "
          f"({len(en)} rows, pairing from {pairs_from})")
    return aligned


def align(dataset_id: str, write: bool, pairs_from: str = None) -> bool:
    en_path, mn_path, en, mn = load(dataset_id)
    if en.shape[1] == 2:
        return align_snapshot(dataset_id, pairs_from or dataset_id.replace("-latest", "-all"), write)
    (ec, ed, ev), (mc, md, mv) = roles(en), roles(mn)
    pairing = category_pairing(dataset_id)
    corresponds = ((mn[mc].values == en[ec].map(pairing).values).all()
                   and (mn[md].astype(str).values == en[ed].astype(str).values).all()
                   and (mn[mv].values == en[ev].values).all())
    if corresponds:
        # Already row-aligned in some order (e.g. by date, then label): keep it.
        print(f"{'aligned':10} {dataset_id} ({len(pairing)} categories)")
        return True

    en_sorted = en.sort_values([ec, ed], kind="stable").reset_index(drop=True)
    keys = pd.DataFrame({mc: en_sorted[ec].map(pairing), md: en_sorted[ed].astype(str)})
    mn_indexed = mn.assign(**{md: mn[md].astype(str)})
    mn_sorted = keys.merge(mn_indexed, on=[mc, md], how="left", validate="one_to_one")[list(mn.columns)]
    assert (mn_sorted[mv].values == en_sorted[ev].values).all()

    aligned = False
    if write:
        en_sorted.to_csv(en_path, index=False)
        mn_sorted.to_csv(mn_path, index=False)
    status = "aligned" if aligned else ("REORDERED" if write else "MISALIGNED")
    print(f"{status:10} {dataset_id} ({len(pairing)} categories)")
    return aligned


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("datasets", nargs="+", help="dataset ids (shell globs over ids are fine)")
    parser.add_argument("--check", action="store_true", help="report only; exit 1 if any are misaligned")
    parser.add_argument("--pairs-from", help="long-format dataset id supplying the pairing for 2-column files")
    args = parser.parse_args()
    ok = all([align(d, write=not args.check, pairs_from=args.pairs_from) for d in args.datasets])
    return 0 if ok or not args.check else 1


if __name__ == "__main__":
    sys.exit(main())
