# -*- coding: utf-8 -*-
"""
Gene Analysis Assistant - Genome Database Downloader
=====================================================
Downloads ClinVar VCF + index files for offline variant annotation.

Usage: python download_data.py
       or double-click download_data.bat

Size: ~184 MB (ClinVar VCF) + ~1 MB (TBI index)
Time: 5-30 minutes depending on network

If auto-download fails, manually download:
  https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
  https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi
  Then place both files in data/clinvar/
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = [
    {
        "name": "ClinVar VCF (GRCh38)",
        "url": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz",
        "path": "data/clinvar/clinvar_grch38.vcf.gz",
        "expected_size": 193012905,  # ~184 MB
    },
    {
        "name": "ClinVar VCF Index (Tabix)",
        "url": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi",
        "path": "data/clinvar/clinvar_grch38.vcf.gz.tbi",
        "expected_size": None,
    },
]

# ---- Helpers ----

def fmt_size(n):
    if n is None:
        return "unknown"
    if n > 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    if n > 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} bytes"


def verify(path, expected_size):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    if size == 0:
        return False
    if expected_size and size < expected_size * 0.95:
        return False
    return True


# ---- Stream download with requests ----

def download_stream(url, outpath, expected_size):
    import requests
    import urllib3
    urllib3.disable_warnings()

    tmp = outpath + ".tmp"
    existing = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    headers = {"User-Agent": "GeneAnalysisAssistant/1.0"}
    resume = existing > 0

    if resume:
        headers["Range"] = f"bytes={existing}-"
        print(f"  Resuming from {fmt_size(existing)}")

    session = requests.Session()
    session.verify = False

    try:
        resp = session.get(url, headers=headers, stream=True, timeout=(30, 900))
    except Exception as e:
        print(f"  Connection error: {e}")
        return False

    if resp.status_code == 200:
        mode = "wb"
        done = 0
    elif resp.status_code == 206:
        mode = "ab"
        done = existing
    elif resp.status_code == 416:
        print("  Already fully downloaded, finalizing...")
        os.rename(tmp, outpath)
        return True
    else:
        print(f"  HTTP {resp.status_code}")
        return False

    total = int(resp.headers.get("Content-Length", 0))
    if total == 0 and expected_size:
        total = expected_size - done

    start = time.time()
    last = 0

    try:
        with open(tmp, mode) as f:
            for chunk in resp.iter_content(chunk_size=1048576):
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                now = time.time()
                if now - last >= 3:
                    elapsed = now - start
                    speed = (done - existing) / elapsed / 1048576 if elapsed > 0 else 0
                    if total > 0:
                        pct = min(done / (existing + total) * 100, 100)
                        print(f"  {done / 1048576:.0f}MB / {(existing + total) / 1048576:.0f}MB ({pct:.0f}%) @ {speed:.1f} MB/s")
                    else:
                        print(f"  {done / 1048576:.1f}MB @ {speed:.1f} MB/s")
                    last = now
    except Exception as e:
        print(f"  Download interrupted: {e}")
        print(f"  Partial file saved ({fmt_size(os.path.getsize(tmp))}). Run again to resume.")
        return False

    # Finalize
    os.rename(tmp, outpath)
    actual = os.path.getsize(outpath)
    elapsed = time.time() - start
    print(f"  Done: {fmt_size(actual)} in {elapsed:.0f}s")

    if expected_size and actual < expected_size * 0.95:
        print(f"  WARNING: File smaller than expected ({fmt_size(actual)} vs {fmt_size(expected_size)})")
        print(f"  Delete {outpath} and retry, or download manually.")
        return False

    return True


def download_urllib(url, outpath):
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlretrieve(url, outpath)
        return os.path.getsize(outpath) > 0
    except Exception as e:
        print(f"  urllib also failed: {e}")
        return False


# ---- Main ----

def main():
    print("=" * 60)
    print("Gene Analysis Assistant - Database Downloader")
    print("=" * 60)
    print(f"Data dir: {DATA_DIR}")
    print()

    # Create dirs
    for sub in ["clinvar", "1000genomes", "giab", "refseq"]:
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)

    # Check requests
    has_requests = False
    try:
        import requests
        has_requests = True
        print("[OK] requests library available (stream + resume supported)")
    except ImportError:
        print("[WARN] requests not installed. Install it for better download reliability:")
        print("       pip install requests")
        print()

    ok = 0
    fail = 0

    for f in FILES:
        outpath = os.path.join(BASE_DIR, f["path"])
        print(f"[Download] {f['name']}")
        print(f"  URL: {f['url']}")
        print(f"  Save to: {f['path']}")

        if verify(outpath, f["expected_size"]):
            print(f"  [SKIP] Already complete ({fmt_size(os.path.getsize(outpath))})")
            ok += 1
            print()
            continue

        if has_requests:
            success = download_stream(f["url"], outpath, f["expected_size"])
        else:
            print("  Using urllib fallback (no resume support)...")
            success = download_urllib(f["url"], outpath)

        if success and verify(outpath, f["expected_size"]):
            ok += 1
        else:
            fail += 1
            print(f"  -> Manual download: {f['url']}")

        print()

    # Summary
    print("=" * 60)
    print(f"Summary: {ok} ok, {fail} failed (of {len(FILES)} files)")
    total = 0
    for root, dirs, files in os.walk(DATA_DIR):
        for fn in files:
            fp = os.path.join(root, fn)
            sz = os.path.getsize(fp)
            total += sz
            rel = os.path.relpath(fp, BASE_DIR)
            print(f"  {rel}: {fmt_size(sz)}")
    print(f"  Total: {fmt_size(total)}")

    if fail > 0:
        print(f"\n[WARN] {fail} file(s) incomplete. Re-run script to resume, or download manually.")
    else:
        print("\n[OK] All files ready. You can start development now.")

    print()
    return fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
