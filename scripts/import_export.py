"""One-shot importer for Medium's official "Download your information" export
(Track B backfill — see SPEC.md section 2, 案1).

NOT YET IMPLEMENTED: Medium's export file format has not been verified against
real data (no export has been requested for medium.com/furuhashilab as of
writing this). Before writing the parser:

1. Have the medium.com/furuhashilab account owner request the export from
   Medium account settings ("Download your information").
2. Extract the resulting archive and inspect its structure, e.g.:
     find <export_dir> -maxdepth 3
3. Update the parsing logic below to match what's actually in the export, then
   remove this NotImplementedError.

Once implemented, this should reuse scripts/lib.py (slugify, content_hash,
write_markdown, load/save_archived_index) so imported posts are indexed and
formatted identically to posts archived by scripts/archive.py (Track A).
"""
import sys
from pathlib import Path


def main(export_dir: str) -> None:
    export_path = Path(export_dir)
    if not export_path.exists():
        raise SystemExit(f"export directory not found: {export_path}")

    raise NotImplementedError(
        f"Inspect the real export structure under {export_path} and "
        "implement parsing here (see module docstring)."
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python import_export.py <path-to-extracted-export>")
    main(sys.argv[1])
