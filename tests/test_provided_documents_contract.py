"""
Fixture harness for the user-provided supporting-documentation change.

SCOPE OF THIS HARNESS -- read before trusting a green run:

The agents in .claude/agents/*.md are Markdown specifications executed by an
LLM, not importable Python modules. This file therefore transcribes the
algorithms specified in those files and exercises them against fixtures. A pass
proves the SPECIFIED LOGIC is self-consistent and handles the required cases.
It does NOT prove an agent at runtime follows the spec -- that requires a live
end-to-end run with Azure DevOps MCP and interactive input.

Transcribed from:
  .claude/agents/qa_workflow_orchestrator.md   Step 2.1d, contract validation, Phase 2 guard
  .claude/agents/md_file_reader.md             Step 0-2, Step 9 leak self-check
  .claude/agents/qa_understanding_doc_creator.md  Step 1, Step 1.4

Run:  python tests/test_provided_documents_contract.py
"""

import json
import sys
import tempfile
from pathlib import Path

SUPPORTED_TYPES = {"API", "UI", "Database", "BusinessLogic", "Integration"}

BUCKET_FOR_TYPE = {
    "API": "apis",
    "Database": "database",
    "BusinessLogic": "businessLogic",
    "UI": "ui",
    "Integration": "integration",
}

NO_DOC_TOKENS = {"none", "no", "n/a", "na", "skip", ""}


class ScopeContractError(Exception):
    pass


# --------------------------------------------------------------------------
# Phase 1 Step 2.1d -- orchestrator
# --------------------------------------------------------------------------
def parse_document_answer(raw_answer, workspace_root="."):
    text = (raw_answer or "").strip()
    if text.lower() in NO_DOC_TOKENS:
        return False, [], []

    resolved, invalid = [], []
    for line in text.splitlines():
        candidate = line.strip().strip('"').strip("'")
        if not candidate:
            continue
        if candidate.lower() in NO_DOC_TOKENS:
            continue

        p = Path(candidate)
        if not p.is_absolute():
            p = (Path(workspace_root) / p).resolve()

        if not p.exists():
            invalid.append({"path": candidate, "reason": "does not exist"})
            continue
        if p.is_dir():
            invalid.append({"path": candidate, "reason": "is a directory, not a file"})
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                fh.read(1)
        except Exception as exc:
            invalid.append({"path": candidate, "reason": f"not readable ({type(exc).__name__})"})
            continue

        resolved.append({
            "path": str(p),
            "as_entered": candidate,
            "exists": True,
            "size_bytes": p.stat().st_size,
        })

    return len(resolved) > 0, resolved, invalid


# --------------------------------------------------------------------------
# Contract validation -- orchestrator
# --------------------------------------------------------------------------
def validate_contract(ctx):
    selected_types = ctx.get("selected_types")
    if not isinstance(selected_types, list) or not selected_types:
        raise ScopeContractError("ABORT: missing or empty 'selected_types'.")

    unsupported = [t for t in selected_types if t not in SUPPORTED_TYPES]
    if unsupported:
        raise ScopeContractError(f"ABORT: unsupported type(s): {unsupported}")

    if "documents_provided" not in ctx:
        raise ScopeContractError("ABORT: missing 'documents_provided'.")
    if not isinstance(ctx["documents_provided"], bool):
        raise ScopeContractError("ABORT: 'documents_provided' must be a bool.")

    docs = ctx.get("provided_documents")
    if not isinstance(docs, list):
        raise ScopeContractError("ABORT: 'provided_documents' must be a list.")

    if ctx["documents_provided"] != (len(docs) > 0):
        raise ScopeContractError(
            f"ABORT: documents_provided={ctx['documents_provided']} but "
            f"{len(docs)} document(s) listed."
        )

    for d in docs:
        if not isinstance(d, dict) or "path" not in d:
            raise ScopeContractError(f"ABORT: malformed provided_documents entry: {d!r}")
        if not Path(d["path"]).is_file():
            raise ScopeContractError(
                f"ABORT: {d['path']} is no longer a readable file. "
                f"Do NOT substitute another file."
            )
    return selected_types


# --------------------------------------------------------------------------
# Phase 2 -- md_file_reader Step 9
# --------------------------------------------------------------------------
def build_integration_docs(selected_types, documents_provided, provided_documents,
                           extracted_by_type):
    """extracted_by_type: {"API": [...], ...} -- only in-scope types may appear."""
    result = {
        "scope": {"selected_types": list(selected_types)},
        "documents_provided": documents_provided,
        "apis": [], "database": [], "businessLogic": [], "ui": [], "integration": [],
        "extraction_gaps": [],
        "out_of_scope_content_seen": [],
        "metadata": {
            "sourceMode": "user-provided (no project scan)",
            "documentCount": len(provided_documents),
            "sources": [d["path"] for d in provided_documents],
        },
    }

    for typ, items in extracted_by_type.items():
        if typ not in selected_types:
            # Discarded, recorded, never emitted into a bucket.
            result["out_of_scope_content_seen"].append(
                {"type": typ, "note": "content present but type not selected; discarded"}
            )
            continue
        result[BUCKET_FOR_TYPE[typ]] = items

    for typ in selected_types:
        if not result[BUCKET_FOR_TYPE[typ]]:
            reason = ("no supporting documentation provided" if not documents_provided
                      else "provided documentation contained no content for this type")
            result["extraction_gaps"].append({"type": typ, "reason": reason})

    # Leak self-check: no out-of-scope bucket may be populated.
    leaked = [t for t, b in BUCKET_FOR_TYPE.items()
              if t not in selected_types and result[b]]
    if leaked:
        raise ScopeContractError(f"ABORT: out-of-scope buckets populated: {leaked}")

    return result


# --------------------------------------------------------------------------
# Phase 3 -- qa_understanding_doc_creator Step 1
# --------------------------------------------------------------------------
def phase3_load(selected_types, integration_file_exists, integration_docs):
    if not integration_file_exists:
        raise ScopeContractError("ABORT: integration-docs.json not found. Phase 2 did not run.")

    doc_scope = integration_docs.get("scope", {}).get("selected_types")
    if doc_scope != selected_types:
        raise ScopeContractError(
            f"ABORT: scope drift. docs say {doc_scope}, contract says {selected_types}."
        )

    gaps = integration_docs.get("extraction_gaps", [])
    open_questions = [
        f"No documentation for {g['type']} ({g['reason']})." for g in gaps
    ]
    return {"proceeded": True, "open_questions": open_questions}


# ==========================================================================
# Checks
# ==========================================================================
RESULTS = []


def check(name, fn):
    try:
        fn()
        RESULTS.append((True, name, ""))
    except AssertionError as e:
        RESULTS.append((False, name, str(e) or "assertion failed"))
    except Exception as e:
        RESULTS.append((False, name, f"{type(e).__name__}: {e}"))


def main():
    tmp = Path(tempfile.mkdtemp(prefix="qa_doc_contract_"))
    api_doc = tmp / "api-spec.md"
    api_doc.write_text("# API\nPOST /things\n", encoding="utf-8")
    db_doc = tmp / "db-schema.md"
    db_doc.write_text("# DB\ntable things\n", encoding="utf-8")
    a_dir = tmp / "somedir"
    a_dir.mkdir()

    # 1. API-only with an API document
    def c1():
        ok, resolved, invalid = parse_document_answer(str(api_doc))
        assert ok and len(resolved) == 1 and not invalid
        ctx = {"selected_types": ["API"], "documents_provided": ok,
               "provided_documents": resolved}
        st = validate_contract(ctx)
        docs = build_integration_docs(st, ok, resolved, {"API": [{"endpoint": "/things"}]})
        assert docs["apis"] and not docs["extraction_gaps"]
        assert docs["ui"] == [] and docs["database"] == []

    # 2. UI-only with a UI document
    def c2():
        ctx = {"selected_types": ["UI"], "documents_provided": True,
               "provided_documents": [{"path": str(api_doc)}]}
        st = validate_contract(ctx)
        docs = build_integration_docs(st, True, ctx["provided_documents"],
                                      {"UI": [{"screen": "Pod View"}]})
        assert docs["ui"] and not docs["apis"]
        assert not docs["extraction_gaps"]

    # 3. selected_types is authoritative: doc content cannot widen it
    def c3():
        st = ["UI"]
        docs = build_integration_docs(st, True, [{"path": str(api_doc)}],
                                      {"UI": [{"screen": "X"}], "API": [{"endpoint": "/y"}]})
        assert docs["scope"]["selected_types"] == ["UI"]
        assert docs["apis"] == [], "API content leaked into scope"
        assert any(o["type"] == "API" for o in docs["out_of_scope_content_seen"])

    # 4. API document supplied during a UI-only run -> API discarded, UI gap raised
    def c4():
        st = ["UI"]
        docs = build_integration_docs(st, True, [{"path": str(api_doc)}],
                                      {"API": [{"endpoint": "/things"}]})
        assert docs["apis"] == []
        assert [g["type"] for g in docs["extraction_gaps"]] == ["UI"]
        assert "no content for this type" in docs["extraction_gaps"][0]["reason"]

    # 5. DB document when Database not selected
    def c5():
        st = ["API"]
        docs = build_integration_docs(st, True, [{"path": str(db_doc)}],
                                      {"API": [{"endpoint": "/t"}], "Database": [{"table": "t"}]})
        assert docs["database"] == []
        assert docs["apis"]

    # 6. No-document path end to end
    def c6():
        ok, resolved, invalid = parse_document_answer("none")
        assert ok is False and resolved == [] and invalid == []
        ctx = {"selected_types": ["API"], "documents_provided": False,
               "provided_documents": []}
        st = validate_contract(ctx)
        docs = build_integration_docs(st, False, [], {})
        assert docs["extraction_gaps"] == [
            {"type": "API", "reason": "no supporting documentation provided"}]
        out = phase3_load(st, True, docs)
        assert out["proceeded"] is True
        assert len(out["open_questions"]) == 1

    # 6b. All no-doc tokens, case-insensitive
    def c6b():
        for tok in ["none", "None", "NONE", " no ", "N/A", "na", "skip", "", "  "]:
            ok, resolved, invalid = parse_document_answer(tok)
            assert ok is False, f"token {tok!r} not treated as no-doc"
            assert resolved == [] and invalid == []

    # 7. Multiple documents
    def c7():
        answer = f"{api_doc}\n{db_doc}"
        ok, resolved, invalid = parse_document_answer(answer)
        assert ok and len(resolved) == 2 and not invalid
        paths = {r["path"] for r in resolved}
        assert str(api_doc.resolve()) in paths or str(api_doc) in paths

    # 8. API + Database together
    def c8():
        st = ["API", "Database"]
        docs = build_integration_docs(st, True, [{"path": str(api_doc)}, {"path": str(db_doc)}],
                                      {"API": [{"endpoint": "/t"}], "Database": [{"table": "t"}]})
        assert docs["apis"] and docs["database"]
        assert not docs["extraction_gaps"]
        assert phase3_load(st, True, docs)["proceeded"]

    # 8b. API + Database, only API documented -> DB gap survives into Phase 3
    def c8b():
        st = ["API", "Database"]
        docs = build_integration_docs(st, True, [{"path": str(api_doc)}],
                                      {"API": [{"endpoint": "/t"}]})
        assert [g["type"] for g in docs["extraction_gaps"]] == ["Database"]
        oq = phase3_load(st, True, docs)["open_questions"]
        assert len(oq) == 1 and "Database" in oq[0]

    # 9. Invalid paths reported, never silently dropped, never substituted
    def c9():
        answer = f"{tmp/'missing.md'}\n{a_dir}\n{api_doc}"
        ok, resolved, invalid = parse_document_answer(answer)
        reasons = {i["reason"] for i in invalid}
        assert len(invalid) == 2, f"expected 2 invalid, got {invalid}"
        assert "does not exist" in reasons
        assert "is a directory, not a file" in reasons
        assert len(resolved) == 1, "valid path must still resolve"
        # Contract must not be written while invalid is non-empty; if it were,
        # documents_provided must still agree with resolved.
        ctx = {"selected_types": ["API"], "documents_provided": ok,
               "provided_documents": resolved}
        validate_contract(ctx)

    # 9b. All paths invalid -> documents_provided False, contract still consistent
    def c9b():
        ok, resolved, invalid = parse_document_answer(str(tmp / "nope.md"))
        assert ok is False and resolved == [] and len(invalid) == 1
        validate_contract({"selected_types": ["API"], "documents_provided": False,
                           "provided_documents": []})

    # 9c. Inconsistent contract is rejected
    def c9c():
        try:
            validate_contract({"selected_types": ["API"], "documents_provided": True,
                               "provided_documents": []})
        except ScopeContractError:
            return
        raise AssertionError("inconsistent contract was accepted")

    # 9d. Vanished file rejected without substitution
    def c9d():
        ghost = tmp / "ghost.md"
        ghost.write_text("x", encoding="utf-8")
        ctx = {"selected_types": ["API"], "documents_provided": True,
               "provided_documents": [{"path": str(ghost)}]}
        validate_contract(ctx)
        ghost.unlink()
        try:
            validate_contract(ctx)
        except ScopeContractError as e:
            assert "substitute" in str(e)
            return
        raise AssertionError("vanished file was accepted")

    # 10. Gaps surface without invention; unsupported type rejected
    def c10():
        st = ["API", "UI", "Database", "BusinessLogic", "Integration"]
        docs = build_integration_docs(st, False, [], {})
        assert len(docs["extraction_gaps"]) == 5
        assert len(phase3_load(st, True, docs)["open_questions"]) == 5
        try:
            validate_contract({"selected_types": ["Security"], "documents_provided": False,
                               "provided_documents": []})
        except ScopeContractError:
            pass
        else:
            raise AssertionError("Category 'Security' accepted as a type")

    # 11. Phase 3 aborts only when Phase 2 truly did not run
    def c11():
        try:
            phase3_load(["API"], False, {})
        except ScopeContractError as e:
            assert "Phase 2 did not run" in str(e)
        else:
            raise AssertionError("missing file did not abort")
        # scope drift
        docs = build_integration_docs(["API"], False, [], {})
        try:
            phase3_load(["UI"], True, docs)
        except ScopeContractError as e:
            assert "scope drift" in str(e)
            return
        raise AssertionError("scope drift not detected")

    check("1  API-only + API doc", c1)
    check("2  UI-only + UI doc", c2)
    check("3  selected_types authoritative (doc cannot widen)", c3)
    check("4  API doc during UI-only run discarded", c4)
    check("5  DB doc when Database not selected", c5)
    check("6  no-document path end to end", c6)
    check("6b no-doc tokens case-insensitive", c6b)
    check("7  multiple documents", c7)
    check("8  API + Database both covered", c8)
    check("8b API + Database, DB gap survives to Phase 3", c8b)
    check("9  invalid paths reported, valid one kept", c9)
    check("9b all paths invalid", c9b)
    check("9c inconsistent contract rejected", c9c)
    check("9d vanished file rejected, no substitution", c9d)
    check("10 gaps surfaced without invention", c10)
    check("11 Phase 3 abort vs proceed", c11)

    print("\nSpecified-logic checks for provided-documents change")
    print("=" * 62)
    for ok, name, err in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if err:
            print(f"        {err}")
    failed = [r for r in RESULTS if not r[0]]
    print("=" * 62)
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    print("\nNOTE: this validates the algorithms as specified in the agent .md")
    print("files. It does NOT verify agent runtime adherence, which needs a live")
    print("end-to-end run with Azure DevOps MCP and interactive input.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
