import argparse, json, os, zipfile, hashlib


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    manifest = {"name": "AutoFire patch", "version": args.version, "files": []}
    with zipfile.ZipFile(args.out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in args.files:
            src = os.path.join(args.project, rel)
            if not os.path.isfile(src):
                raise SystemExit(f"Not found: {src}")
            z.write(src, arcname=rel)
            manifest["files"].append(
                {
                    "path": rel.replace("\\", "/"),
                    "sha256": sha256_file(src),
                    "bytes": os.path.getsize(src),
                }
            )
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
