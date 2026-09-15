"""
Migrate existing flat outputs/<PBI>/ folders to the standard three-bucket layout.

    outputs/<PBI>/{deliverables,working,logs}

Non-destructive: nothing is deleted. Superseded duplicates, scratch runs, and
stale artifacts from earlier runs are MOVED to archive/, not removed.

Dry-run by default. Pass --apply to actually move files.

    python scripts/migrate_outputs.py                      # preview everything
    python scripts/migrate_outputs.py --pbi 643243         # preview one PBI
    python scripts/migrate_outputs.py --apply              # do it
    python scripts/migrate_outputs.py --pbi 643243 --stale-before 2026-09-11 --apply

--stale-before marks DELIVERABLES older than the given date as superseded, for
the case where a folder mixes a fresh run with leftovers from an older one.
Working and log files are never treated as stale; they are simply filed.

Re-running is safe: files already in deliverables/working/logs are left alone.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
OUTPUTS = REPO / "outputs"
ARCHIVE = REPO / "archive" / "outputs"

STANDARD_DIRS = {"deliverables", "working", "logs"}

# Scratch/test run folders — kept, but out of the way.
SCRATCH_RE = re.compile(r"^(TEST\d*|SCRATCH.*|TMP.*)$", re.IGNORECASE)

# ------------------------------------------------------------------ buckets
WORKING_EXACT = {
    "pbi-data.json",
    "user-context.json",
    "integration-docs.json",
    "qa_doc_extract.json",
    "qa-doc-extract.json",
    "scenarios_parsed.json",
    "scenarios-parsed.json",
    "scenarios_for_test_cases.json",
    "test_cases_generated.json",
    "test-cases-generated.json",
    "template_structure.json",
}

LOG_TOKENS = ("summary", "report", "review", "validation", "quality", "phase")

# Canonical deliverable per family. Anything else in the family is superseded.
def canonical_names(pbi: str) -> dict[str, str]:
    return {
        "qa_doc": "QA_Understanding_Document.docx",
        "scenarios": "Test-Scenarios-Mapped-to-AC.xlsx",
        "test_cases": f"Test_Cases_PBI_{pbi}.xlsx",
    }


def family_of(name: str) -> str | None:
    low = name.lower()
    if low.endswith(".docx") and "qa_understanding" in low:
        return "qa_doc"
    if low.endswith(".xlsx"):
        if "scenario" in low:
            return "scenarios"
        if "test_cases" in low or "test-cases" in low:
            return "test_cases"
    return None


def classify(path: Path, pbi: str) -> str:
    """Return one of: deliverables, working, logs, archive."""
    name = path.name
    low = name.lower()

    # Excel/Word lock and temp files.
    if name.startswith("~$") or low.endswith((".tmp", ".bak")):
        return "archive"
    # Explicit generator backups kept only for history.
    if low.endswith((".old", ".previous", ".backup")):
        return "archive"

    if name in WORKING_EXACT:
        return "working"

    # Generated helper scripts live with the run that produced them.
    if low.endswith((".py", ".js", ".sh")):
        return "working"

    if family_of(name):
        return "deliverables"

    if low.endswith((".md", ".txt")):
        if any(tok in low for tok in LOG_TOKENS):
            return "logs"
        # Legacy markdown copies of the QA doc, superseded by .docx.
        if "qa-understanding" in low or "qa_understanding" in low:
            return "archive"
        return "logs"

    if low.endswith(".json"):
        return "working"

    # Unknown extension: file under working rather than guessing it is final.
    return "working"


def plan_for_pbi(pbi_dir: Path, stale_before: datetime | None) -> list[tuple[Path, Path, str]]:
    """Return [(src, dst, reason)]. Empty list means nothing to do."""
    pbi = pbi_dir.name
    moves: list[tuple[Path, Path, str]] = []

    if SCRATCH_RE.match(pbi):
        dst = ARCHIVE / "scratch-runs" / pbi
        return [(pbi_dir, dst, "scratch/test run folder")]

    loose = [p for p in pbi_dir.iterdir() if p.is_file()]
    if not loose:
        return []

    canon = canonical_names(pbi)

    # Resolve deliverable families: newest canonical wins, rest are superseded.
    best: dict[str, Path] = {}
    for p in loose:
        fam = family_of(p.name)
        if not fam:
            continue
        cur = best.get(fam)
        if cur is None:
            best[fam] = p
            continue
        # Newest content wins, then gets renamed to the canonical filename.
        # Preferring the canonical NAME instead would archive a more recent
        # regeneration purely because it was saved under a variant name.
        if p.stat().st_mtime > cur.stat().st_mtime:
            best[fam] = p
        elif p.stat().st_mtime == cur.stat().st_mtime and p.name == canon[fam]:
            best[fam] = p

    for p in sorted(loose):
        bucket = classify(p, pbi)
        reason = f"classified as {bucket}"
        fam = family_of(p.name)

        if bucket == "deliverables" and fam:
            if best.get(fam) is not p:
                bucket, reason = "archive", f"superseded {fam} (kept: {best[fam].name})"
            elif stale_before and datetime.fromtimestamp(p.stat().st_mtime) < stale_before:
                bucket, reason = (
                    "archive",
                    f"predates current run ({datetime.fromtimestamp(p.stat().st_mtime):%Y-%m-%d})",
                )

        if bucket == "archive":
            dst = ARCHIVE / pbi / p.name
        else:
            dst = pbi_dir / bucket / (canon[fam] if (bucket == "deliverables" and fam) else p.name)
            if bucket == "deliverables" and fam and p.name != canon[fam]:
                reason += f"; renamed to canonical {canon[fam]}"

        moves.append((p, dst, reason))

    return moves


def execute(moves, apply: bool) -> tuple[int, int]:
    moved = skipped = 0
    for src, dst, reason in moves:
        rel_src = src.relative_to(REPO)
        rel_dst = dst.relative_to(REPO)
        if not src.exists():
            continue
        if dst.exists() and dst.resolve() != src.resolve():
            print(f"  SKIP   {rel_src}\n         -> {rel_dst} (destination exists)")
            skipped += 1
            continue
        print(f"  MOVE   {rel_src}\n         -> {rel_dst}\n         ({reason})")
        if apply:
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
            except (PermissionError, OSError) as exc:
                # Typically an .xlsx still open in Excel. Leave it in place and
                # keep going; re-running the migration will pick it up.
                print(f"         LOCKED — left in place ({type(exc).__name__}). "
                      f"Close the file and re-run.")
                skipped += 1
                continue
        moved += 1
    return moved, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pbi", help="Migrate only this PBI folder")
    ap.add_argument("--apply", action="store_true", help="Actually move files")
    ap.add_argument("--stale-before", metavar="YYYY-MM-DD",
                    help="Archive deliverables older than this date")
    args = ap.parse_args()

    stale = datetime.strptime(args.stale_before, "%Y-%m-%d") if args.stale_before else None

    if not OUTPUTS.is_dir():
        print(f"No outputs/ directory at {OUTPUTS}")
        return 0

    targets = ([OUTPUTS / args.pbi] if args.pbi
               else sorted(p for p in OUTPUTS.iterdir() if p.is_dir()))

    mode = "APPLY" if args.apply else "DRY RUN (nothing will be moved)"
    print(f"Output migration — {mode}")
    print("=" * 70)

    total_moved = total_skipped = 0
    for pbi_dir in targets:
        if not pbi_dir.is_dir():
            print(f"\n{pbi_dir.name}: not found")
            continue
        moves = plan_for_pbi(pbi_dir, stale)
        print(f"\n{pbi_dir.name}/  ({len(moves)} action(s))")
        if not moves:
            print("  already standard-compliant")
            continue
        m, s = execute(moves, args.apply)
        total_moved += m
        total_skipped += s

    # Loose files sitting directly in outputs/ (not inside any PBI folder).
    if not args.pbi:
        loose_root = [p for p in OUTPUTS.iterdir() if p.is_file()]
        if loose_root:
            print(f"\noutputs/ (loose files, {len(loose_root)})")
            m, s = execute([(p, ARCHIVE / "_root" / p.name, "loose file in outputs/")
                            for p in sorted(loose_root)], args.apply)
            total_moved += m
            total_skipped += s

    print("\n" + "=" * 70)
    print(f"{total_moved} move(s), {total_skipped} skipped")
    if not args.apply:
        print("Dry run only. Re-run with --apply to perform these moves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
