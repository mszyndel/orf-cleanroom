#!/usr/bin/env python3
"""List and validate the verified findings in findings/.

Supports: findings/README.md (file format and status rules), CONTRIBUTING.md.
Standard library only. A finding is a lead that a DIFFERENT person reproduced.
Leads themselves are GitHub issues labelled `lead`, not files. Each finding file
names the finder (`Author:`, also in the file name), the reproducer
(`Verified by:`) and the lead issue (`Lead: #<n>`). Status:
  verified    nobody has corrected it
  superseded  a later verified finding lists it in `Corrects:`

Validation (--check): file name pattern, Author matches the handle in the file
name, Verified by is a different handle, Lead is `#<n>`, Variant matches the
folder, required sections present, `Builds on:` / `Corrects:` entries are finding
IDs that exist or `#<n>` issue numbers (accepted without lookup). Exits 1 on errors.

Usage: python findings_index.py [--root DIR] [--check]
"""
import argparse
import datetime
import os
import re
import sys

FOLDER_RE = re.compile(r"^(container|unassigned|V[0-9]+)$")
NAME_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})--([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)--([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
ID_PATTERN = r"(?:\d{4}-\d{2}-\d{2}--[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*--[a-z0-9]+(?:-[a-z0-9]+)*|#[0-9]+)"
REF_RE = re.compile(r"^(" + ID_PATTERN + r")$")
KEY_RE = re.compile(r"^([A-Z][A-Za-z ]*):\s*(.*)$")
KNOWN_KEYS = ["Author", "Verified by", "Lead", "Variant", "Builds on", "Corrects"]
REF_KEYS = ["Builds on", "Corrects"]
SECTIONS = ["Claim", "Original evidence", "Verification", "Reproduce"]
HANDLE_RE = re.compile(r"^@([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)$")
LEAD_RE = re.compile(r"^#[0-9]+$")


class Finding:
    def __init__(self, fid, folder, path, author, title, verifier=""):
        self.id, self.folder, self.path = fid, folder, path
        self.author, self.title, self.verifier = author, title, verifier
        self.refs = {k: [] for k in REF_KEYS}


def folder_key(name):
    if name == "container":
        return (0, 0)
    if name == "unassigned":
        return (2, 0)
    return (1, int(name[1:]))


def parse_file(path, folder, name, found, errors):
    def err(msg):
        errors.append("%s: %s" % (path, msg))

    m = NAME_RE.match(name)
    if not m:
        err("file name must be YYYY-MM-DD--handle--short-slug.md (lowercase slug, no spaces)")
        return
    try:
        datetime.date(*[int(x) for x in m.group(1).split("-")])
    except ValueError:
        err("date in the file name is not a real date")
        return
    fid, handle = name[:-3], m.group(2)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().replace("\r\n", "\n").split("\n")
    except (OSError, UnicodeDecodeError) as e:
        err("cannot read as UTF-8 text: %s" % e)
        return
    title = ""
    if lines and lines[0].startswith("# ") and lines[0][2:].strip():
        title = lines[0][2:].strip()
    else:
        err("first line must be '# <title>'")
    header, headings = {}, []
    in_header = True
    for line in lines[1:]:
        if line.startswith("## "):
            in_header = False
            headings.append(line[3:].strip())
        elif in_header and not line.strip():
            if header:  # the header block ends at the first blank line after its first key
                in_header = False
        elif in_header:
            km = KEY_RE.match(line)
            if km:
                key, val = km.group(1), km.group(2).strip()
                if key not in KNOWN_KEYS:
                    print("WARN %s: unknown header line '%s:' (ignored)" % (path, key))
                elif key in header:
                    err("'%s:' appears twice" % key)
                else:
                    header[key] = val
    for sec in SECTIONS:
        if not any(h == sec or h.startswith(sec + " ") for h in headings):
            err("missing section '## %s'" % sec)
    author = header.get("Author", "")
    am = HANDLE_RE.match(author)
    if not am:
        err("'Author: @handle' line is missing or malformed")
    elif am.group(1).lower() != handle.lower():
        err("Author %s does not match the handle '%s' in the file name" % (author, handle))
    verifier = header.get("Verified by", "")
    vm = HANDLE_RE.match(verifier)
    if not vm:
        err("'Verified by: @handle' line is missing or malformed")
    elif am and vm.group(1).lower() == am.group(1).lower():
        err("Verified by must be a different person than Author (nobody verifies their own lead)")
    if not LEAD_RE.match(header.get("Lead", "")):
        err("'Lead: #<issue number>' line is missing or malformed")
    variant = header.get("Variant", "")
    if variant != folder:
        err("Variant '%s' does not match the folder '%s'" % (variant, folder))
    f = Finding(fid, folder, path, handle, title, vm.group(1) if vm else "")
    for key in REF_KEYS:
        for part in header.get(key, "").split(","):
            part = part.strip()
            if not part:
                continue
            if not REF_RE.match(part):
                err("'%s:' entry is not a finding ID or #issue: %s" % (key, part))
            else:
                f.refs[key].append(part)
    found[fid] = f


def scan(root, found, errors):
    base = os.path.join(root, "findings")
    if not os.path.isdir(base):
        return
    for entry in sorted(os.listdir(base)):
        p = os.path.join(base, entry)
        if os.path.isfile(p):
            if entry != "README.md":
                errors.append("%s: stray file; findings go in a variant folder" % p)
            continue
        if not FOLDER_RE.match(entry):
            errors.append("%s: unknown folder (use container, V<n> or unassigned)" % p)
            continue
        for name in sorted(os.listdir(p)):
            fp = os.path.join(p, name)
            if os.path.isdir(fp):
                errors.append("%s: sub-folders are not allowed" % fp)
            elif name != "README.md":
                parse_file(fp, entry, name, found, errors)


def resolve(found, errors):
    for f in found.values():
        for key in REF_KEYS:
            ok = []
            for ref in f.refs[key]:
                if ref.startswith("#"):
                    ok.append(ref)  # issue numbers are not looked up
                elif ref not in found:
                    errors.append("%s: '%s:' refers to unknown finding %s" % (f.path, key, ref))
                elif ref == f.id:
                    errors.append("%s: '%s:' refers to itself" % (f.path, key))
                else:
                    ok.append(ref)
            f.refs[key] = ok


def statuses(found):
    """id -> (status, superseded_by); a later finding that lists it in `Corrects:` supersedes it."""
    out = {}
    for fid, f in found.items():
        sup = [g for g in found.values() if fid in g.refs["Corrects"]]
        out[fid] = ("superseded" if sup else "verified", sup)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 epilog="Leads are GitHub issues labelled `lead`; this lists only findings "
                                        "(leads a different person verified).")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
                    help="repo root (default: the repo this script is in)")
    ap.add_argument("--check", action="store_true",
                    help="validate only: print problems, exit 1 if any (no index)")
    args = ap.parse_args()

    found, errors = {}, []
    scan(args.root, found, errors)
    resolve(found, errors)
    for e in errors:
        print("ERROR " + e)
    if args.check:
        if errors:
            sys.exit(1)
        print("ok: %d findings" % len(found))
        return

    st = statuses(found)
    if not found:
        print("No verified findings yet. Leads are open issues labelled `lead`.")
    for folder in sorted({f.folder for f in found.values()}, key=folder_key):
        items = sorted((f for f in found.values() if f.folder == folder), key=lambda f: f.id)
        print("%s (%d)" % (folder, len(items)))
        for f in items:
            status, sup = st[f.id]
            by = "  verified by @%s" % f.verifier if f.verifier else ""
            print("  %s  @%s  %s  %s%s" % (f.id, f.author, status, f.title, by))
            if sup:
                print("      superseded by: " + ", ".join("%s (@%s)" % (g.id, g.author) for g in sup))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
