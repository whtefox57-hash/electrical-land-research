"""Regenerate outputs/DATA_STATUS.md from the append-only attempt log.

Every dataset attempt is recorded — URL, UTC timestamp, success or the exact
error text, and a manual download URL. Failures are listed first because they
are the ones that change how the outputs should be read.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, OUTPUTS, STATUS_LOG


def main():
    if not os.path.exists(STATUS_LOG):
        print("no status log yet")
        return
    recs = [json.loads(l) for l in open(STATUS_LOG) if l.strip()]

    # Keep the LAST attempt per dataset KEY, so a successful retry supersedes
    # the earlier failure instead of leaving a phantom failure behind.
    latest: dict[str, dict] = {}
    for r in recs:
        latest[r.get("key") or r["dataset"]] = r
    ok = [r for r in latest.values() if r["status"] == "SUCCESS"]
    bad = [r for r in latest.values() if r["status"] != "SUCCESS"]

    out = []
    out.append("# DATA_STATUS — every dataset attempted\n")
    out.append(f"Regenerated {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC "
               f"from `data/data_status_log.jsonl` ({len(recs)} attempt "
               f"records, {len(latest)} distinct datasets).\n")
    out.append(f"**{len(ok)} succeeded · {len(bad)} failed (final state).**\n")
    out.append("A dataset listed as SUCCESS here was read from the network in "
               "this run. Nothing in this project is estimated, synthesised or "
               "substituted: where a source failed, the dependent field is left "
               "empty and the failure is recorded below.\n")

    out.append("\n---\n")
    out.append("\n## FAILED — unresolved\n")
    if not bad:
        out.append("\nNone. Every dataset attempted was retrieved.\n")
    else:
        for r in sorted(bad, key=lambda x: x["dataset"]):
            out.append(f"\n### {r['dataset']}\n")
            out.append(f"- **Attempted:** `{r['url']}`\n")
            out.append(f"- **Timestamp:** {r['timestamp']}\n")
            out.append(f"- **Error:** `{r['detail']}`\n")
            out.append(f"- **Manual download:** {r['manual_download_url']}\n")

    out.append("\n---\n")
    out.append("\n## SUCCEEDED\n")
    out.append("\n| dataset | records | timestamp (UTC) | endpoint |\n")
    out.append("|---|---:|---|---|\n")
    for r in sorted(ok, key=lambda x: x["dataset"]):
        n = r.get("records")
        out.append(f"| {r['dataset']} | {n if n is not None else ''} | "
                   f"{r['timestamp']} | `{r['url']}` |\n")

    # Full chronological history, including superseded failures.
    superseded = [r for r in recs
                  if r["status"] != "SUCCESS"
                  and latest.get(r.get("key") or r["dataset"], {}
                                 ).get("status") == "SUCCESS"]
    if superseded:
        out.append("\n---\n")
        out.append("\n## Failures later resolved by retry\n")
        out.append("\nRecorded so the diagnosis is not lost. Each of these "
                   "failed first, was diagnosed, and then succeeded on a "
                   "corrected request.\n")
        for r in superseded:
            out.append(f"\n- **{r['dataset']}** — {r['timestamp']}\n"
                       f"  - error: `{r['detail'][:400]}`\n")

    with open(os.path.join(OUTPUTS, "DATA_STATUS.md"), "w") as fh:
        fh.write("".join(out))
    print(f"wrote outputs/DATA_STATUS.md — {len(ok)} ok, {len(bad)} failed")


if __name__ == "__main__":
    main()
