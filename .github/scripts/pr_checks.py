#!/usr/bin/env python3
"""Pull request checks for findings/, FINDINGS.md and samples/manifest.csv.

FINDINGS.md may be deleted only after its F<n> entries moved verbatim into added
findings files with matching Alias and Author (check_migration). Standard library
only (Python 3.8+). Run from the repo root with the PR merged
into the work tree. Environment: BASE (base commit SHA), PR_AUTHOR (login),
FINDINGS_INDEX (optional path to the findings_index.py to run; CI passes the
copy from the base branch so a PR cannot change its own validator).
Prints GitHub Actions annotations. Exits 1 on any error; warnings don't fail.
"""
import csv
import os
import re
import subprocess
import sys

# Locally: python .github/scripts/pr_checks.py after committing (BASE defaults to origin/main).
BASE = os.environ.get("BASE", "origin/main")
AUTHOR = os.environ.get("PR_AUTHOR", "")
INDEX = os.environ.get("FINDINGS_INDEX", "tools/findings_index.py")
NOTE = "## Frozen: new findings go in findings/"
HANDLE = re.compile(r"^@[A-Za-z0-9]+(?:-[A-Za-z0-9]+)* ")
errors = []


def error(path, msg):
    errors.append(msg)
    print("::error file=%s::%s" % (path, msg))


def warning(path, msg):
    print("::warning file=%s::%s" % (path, msg))


def git(*args):
    return subprocess.run(["git"] + list(args), stdout=subprocess.PIPE, check=True).stdout


def base_file(path, rev=None):
    try:
        return subprocess.run(["git", "show", "%s:%s" % (rev or BASE, path)], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, check=True).stdout
    except subprocess.CalledProcessError:
        return None


ENTRY = re.compile(r"^## (F[0-9]+) \(\d{4}-\d{2}-\d{2}, (@[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\): .*$")
ALIAS = re.compile(r"^Alias:[ \t]*(F[0-9]+)[ \t]*$", re.M)
AUTHOR_LINE = re.compile(r"^Author:[ \t]*(@\S+)[ \t]*$", re.M)


def norm(text):
    return " ".join(text.split())


def legacy_entries(text):
    """FINDINGS.md text -> {id: (handle, body)}; body = lines after the heading up to the next '## '."""
    out, cur = {}, None
    for line in text.splitlines():
        m = ENTRY.match(line)
        if m:
            cur = m.group(1)
            out[cur] = [m.group(2), []]
        elif line.startswith("## "):
            cur = None
        elif cur:
            out[cur][1].append(line)
    return dict((k, (v[0], norm("\n".join(v[1])))) for k, v in out.items())


def file_head(path):
    """Text of a file at HEAD before its first '## ' heading (title and header lines), and the whole text."""
    text = (base_file(path, "HEAD") or b"").decode("utf-8", "replace").replace("\r\n", "\n")
    return text.split("\n## ", 1)[0], text


def check_migration(added):
    """FINDINGS.md deletion: every base entry must be in an added file with its Alias, Author and body."""
    entries = legacy_entries((base_file("FINDINGS.md") or b"").decode("utf-8"))
    if not entries:
        return error("FINDINGS.md", "FINDINGS.md was deleted, but no F<n> entries were found in the base copy.")
    files = {}
    for path in added:
        head, text = file_head(path)
        m = ALIAS.search(head)
        if m:
            files.setdefault(m.group(1), []).append((head, text))
    for fid, (handle, body) in sorted(entries.items()):
        ok = False
        for head, text in files.get(fid, []):
            a = AUTHOR_LINE.search(head)
            if a and a.group(1).lower() == handle.lower() and body in norm(text):
                ok = True
        if not ok:
            error("FINDINGS.md", "FINDINGS.md can only be deleted once %s is in an added findings file with "
                                 "'Alias: %s', 'Author: %s' and the entry's text verbatim." % (fid, fid, handle))


def check_aliases(added):
    """A new file may only claim the alias of a legacy entry that has not moved yet."""
    legacy = set(legacy_entries((base_file("FINDINGS.md") or b"").decode("utf-8")))
    taken = set()
    tree = git("ls-tree", "-r", "--name-only", BASE, "findings/").decode("utf-8").splitlines()
    for line in tree:
        if line.endswith(".md") and not line.endswith("/README.md"):
            m = ALIAS.search((base_file(line) or b"").decode("utf-8", "replace").replace("\r\n", "\n")
                             .split("\n## ", 1)[0])
            if m:
                taken.add(m.group(1))
    for path in added:
        m = ALIAS.search(file_head(path)[0])
        if not m:
            continue
        if m.group(1) in taken:
            error(path, "Alias %s is already taken by another finding." % m.group(1))
        elif m.group(1) not in legacy:
            error(path, "Alias %s is reserved for the first findings (F1-F4) and is not available." % m.group(1))


def check_frozen(changes):
    changed = [p for _, p in changes]
    added = [p for s, p in changes if s == "A" and p.startswith("findings/") and not p.endswith("/README.md")]
    check_aliases(added)
    if "FINDINGS.md" not in changed:
        return
    old = base_file("FINDINGS.md") or b""
    try:
        with open("FINDINGS.md", "rb") as f:
            new = f.read()
    except OSError:
        return check_migration(added)
    if NOTE.encode() in old:
        return error("FINDINGS.md", "FINDINGS.md is frozen. Add a file under findings/ instead "
                                    "(see findings/README.md).")
    tail = new[len(old):].lstrip(b"\n")
    if (not new.startswith(old) or not tail.startswith(NOTE.encode())
            or len(tail) > 1000 or b"\n## " in tail):
        error("FINDINGS.md", "FINDINGS.md may only get the one closing note appended. "
                             "Add findings under findings/ instead.")


def check_findings(changes):
    added = []
    for status, path in changes:
        if not path.startswith("findings/") or path.endswith("/README.md"):
            continue
        if status == "A":
            added.append(path)
        else:
            error(path, "Existing findings are never modified, renamed or deleted (status %s). "
                        "Add a new file with 'Corrects:' instead." % status)
    if added:
        r = subprocess.run([sys.executable, INDEX, "--check", "--root", "."], stdout=subprocess.PIPE,
                           universal_newlines=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            for line in r.stdout.splitlines():
                if line.startswith("ERROR "):
                    print("::error::" + line[6:])
            errors.append("findings_index.py --check failed")
    for path in added:
        parts = os.path.basename(path).split("--")
        if len(parts) == 3 and AUTHOR and parts[1].lower() != AUTHOR.lower():
            warning(path, "File name handle @%s differs from the PR author @%s. Reviewer: check the author "
                          "agreed and the file has 'Submitted by: @%s'." % (parts[1], AUTHOR, AUTHOR))


def check_manifest(changes):
    path = "samples/manifest.csv"
    if path not in [p for _, p in changes]:
        return
    old = base_file(path)
    if old is None:
        return error(path, "samples/manifest.csv is missing on the base branch.")
    # Check what is committed, not the working copy (which may have CRLF on Windows).
    new = base_file(path, "HEAD")
    if new is None:
        return error(path, "samples/manifest.csv was deleted.")
    if not new.startswith(old):
        return error(path, "Existing manifest rows were changed or removed. Rows are append-only: "
                           "add a new row for the same sha256 instead (see samples/README.md).")
    if not old.endswith(b"\n"):
        return error(path, "The old manifest does not end with a newline, so rows cannot be appended.")
    tail = new[len(old):]
    if b"\r" in tail:
        return error(path, "New manifest rows must use LF line endings, not CRLF.")
    if tail and not tail.endswith(b"\n"):
        return error(path, "The last manifest row must end with a newline.")
    header = next(csv.reader(old.decode("utf-8").splitlines()[:1]), None)
    if not header:
        return error(path, "The manifest header line is missing.")
    col = dict((name, i) for i, name in enumerate(header))
    for n, line in enumerate(tail.decode("utf-8").split("\n")[:-1], 1):
        row = next(csv.reader([line]), [])
        where = "new row %d" % n
        if len(row) != len(header):
            error(path, "%s has %d columns, the header has %d." % (where, len(row), len(header)))
            continue
        if not re.match(r"^[0-9a-f]{64}$", row[col["sha256"]]):
            error(path, "%s: sha256 must be 64 lowercase hex characters." % where)
        source, licence, pid = row[col["source"]], row[col["licence"]], row[col["pixls_id"]]
        if source == "pixls":
            if licence != "CC0" or not pid.isdigit():
                error(path, "%s: source pixls needs licence CC0 and a numeric pixls_id." % where)
        elif source == "own":
            if licence != "not-shared" or pid != "":
                error(path, "%s: source own needs licence not-shared and an empty pixls_id." % where)
        else:
            error(path, "%s: source must be pixls or own." % where)
        by = row[col["measured_by"]]
        if not HANDLE.match(by):
            error(path, "%s: measured_by must start with '@handle '." % where)
        elif AUTHOR and by.split(" ")[0].lower() != "@" + AUTHOR.lower():
            warning(path, "%s: measured_by %s differs from the PR author @%s. Reviewer: check the handle."
                    % (where, by.split(" ")[0], AUTHOR))


def main():
    out = git("diff", "--name-status", "--no-renames", "%s...HEAD" % BASE).decode("utf-8")
    changes = [tuple(l.split("\t", 1)) for l in out.splitlines() if "\t" in l]
    check_frozen(changes)
    check_findings(changes)
    check_manifest(changes)
    if errors:
        print("%d problem(s) found." % len(errors))
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
