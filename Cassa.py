import os
import fnmatch

ROOT = "."
OUTPUT = "structure.txt"
IGNORE_FILE = ".pyignore"
INCLUDE_EXT = {".py"}


def load_config():
    ignore = []
    tree_only = []
    section = "ignore"

    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line == "[tree-only]":
                    section = "tree-only"
                    continue
                if section == "ignore":
                    ignore.append(line)
                else:
                    tree_only.append(line)

    return ignore, tree_only


IGNORE_RULES, TREE_ONLY_RULES = load_config()


def match(path, rules):
    path = path.replace("\\", "/")
    for rule in rules:
        if rule.endswith("/") and path.startswith(rule[:-1]):
            return True
        if fnmatch.fnmatch(path, rule):
            return True
    return False


def build_tree(path, prefix=""):
    lines = []
    entries = sorted(os.listdir(path))

    entries = [
        e for e in entries
        if not match(os.path.relpath(os.path.join(path, e), ROOT), IGNORE_RULES)
    ]

    for i, name in enumerate(entries):
        full = os.path.join(path, name)
        rel = os.path.relpath(full, ROOT)

        last = i == len(entries) - 1
        connector = "└── " if last else "├── "
        lines.append(prefix + connector + name)

        if os.path.isdir(full):
            if match(rel + "/", TREE_ONLY_RULES):
                continue  # show folder but do NOT descend

            extension = "    " if last else "│   "
            lines.extend(build_tree(full, prefix + extension))

    return lines


def collect_files():
    files = []

    for root, dirs, filenames in os.walk(ROOT):
        rel_root = os.path.relpath(root, ROOT)

        if rel_root != "." and (
            match(rel_root + "/", IGNORE_RULES)
            or match(rel_root + "/", TREE_ONLY_RULES)
        ):
            dirs[:] = []
            continue

        for file in filenames:
            rel = os.path.join(rel_root, file)
            if match(rel, IGNORE_RULES):
                continue
            if os.path.splitext(file)[1] in INCLUDE_EXT:
                files.append(os.path.join(root, file))

    return files


def write_output():
    with open(OUTPUT, "w", encoding="utf-8") as out:
        out.write(".\n")
        for line in build_tree(ROOT):
            out.write(line + "\n")

        out.write("\n" + "=" * 60 + "\n")
        out.write("FILE CONTENTS\n")
        out.write("=" * 60 + "\n\n")

        for file in collect_files():
            rel = os.path.relpath(file, ROOT)
            out.write(f"--- FILE: {rel} ---\n")
            try:
                with open(file, "r", encoding="utf-8") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"[ERROR: {e}]")
            out.write("\n\n")


if __name__ == "__main__":
    write_output()
    print("✅ structure.txt created with tree-only folders support")