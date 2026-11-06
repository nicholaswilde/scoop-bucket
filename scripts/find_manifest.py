import difflib
import os
import sys


def find_manifest(query, bucket_dir="bucket"):
    manifests = [f[:-5] for f in os.listdir(bucket_dir) if f.endswith(".json")]

    if not query:
        return None, manifests

    # Exact match
    if query in manifests:
        return query, manifests

    # Substring match fallback
    for m in manifests:
        if query in m:
            return m, manifests

    # Best guess using difflib
    matches = difflib.get_close_matches(query, manifests, n=1, cutoff=0.4)
    if matches:
        return matches[0], manifests

    return None, manifests


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    match, all_manifests = find_manifest(query)
    if match:
        print(f"MATCH: {match}")
    else:
        print("NO MATCH")
        print("Available manifests:", ", ".join(all_manifests))
