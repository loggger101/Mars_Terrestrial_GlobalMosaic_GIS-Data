# -*- coding: utf-8 -*-
"""Checks what the repository points at but does not hold. Runs in CI every Monday and by hand.

    python tools/check_remote.py

1. Every release asset matches its release's SHA256SUMS file: same hash as GitHub's own digest,
   nothing missing from the file, nothing in the file missing from the release.
2. Every release the project pages link to exists.
3. The four source mosaics are still served at the README's addresses, at the exact sizes the
   project drive holds (a HEAD request each; nothing is downloaded but the small SHA256SUMS files).

Uses GITHUB_TOKEN if set (CI sets it), so API calls aren't rate-limited. Exit code 1 and a list of
failures if anything is wrong. Stdlib only.
"""
import json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data"
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "exports" / "README.md"]
# Byte sizes of the source mosaics on the project drive (Z:\), 2026-10-08.
SOURCES = {
    "Mars_Viking_MDIM21_ClrMosaic_global_232m.tif": 12_742_411_029,
    "Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif": 22_769_567_365,
    "Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif": 15_179_427_309,
    "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif": 11_384_463_908,
}
fails = []


def request(url, method="GET", accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": "check_remote.py"}
    if os.environ.get("GITHUB_TOKEN") and url.startswith("https://api.github.com/"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers, method=method), timeout=60)


def releases():
    with request(f"https://api.github.com/repos/{REPO}/releases?per_page=100") as r:
        rels = json.load(r)
    n = 0
    for rel in rels:
        assets = {a["name"]: a for a in rel["assets"]}
        sums = [a for name, a in assets.items() if name.startswith("SHA256SUMS")]
        if len(sums) != 1:
            fails.append(f"{rel['tag_name']}: expected one SHA256SUMS file, found {len(sums)}")
            continue
        with request(sums[0]["url"], accept="application/octet-stream") as r:
            listed = {}
            for line in r.read().decode("utf-8").splitlines():
                if line.strip() and "(reassembled" not in line:   # whole-file hashes of split rasters
                    h, name = line.split(None, 1)
                    listed[name.strip()] = h
        for name, a in assets.items():
            if a is sums[0]:
                continue
            n += 1
            digest = (a.get("digest") or "").removeprefix("sha256:")
            if name not in listed:
                fails.append(f"{rel['tag_name']}: {name} is not in {sums[0]['name']}")
            elif digest != listed[name]:
                fails.append(f"{rel['tag_name']}: {name} hash {digest[:12]} != {listed[name][:12]} in the sums")
        for name in set(listed) - set(assets):
            fails.append(f"{rel['tag_name']}: {sums[0]['name']} lists {name}, which the release lacks")
    tags = {rel["tag_name"] for rel in rels}
    for page in PAGES:
        for tag in set(re.findall(rf"github\.com/{REPO}/releases/(?:tag|download)/([^/)\s]+)", page.read_text(encoding="utf-8"))):
            if tag not in tags:
                fails.append(f"{page.relative_to(ROOT)} links release {tag}, which does not exist")
    return n


def sources():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name, size in SOURCES.items():
        m = re.search(r"\]\((https://[^)\s]+/" + re.escape(name) + r")\)", readme)
        if not m:
            fails.append(f"README has no link for {name}")
            continue
        try:
            with request(m.group(1), method="HEAD", accept="*/*") as r:
                got = int(r.headers.get("Content-Length", -1))
        except Exception as e:
            fails.append(f"{name}: {m.group(1)} unreachable ({e})")
            continue
        if got != size:
            fails.append(f"{name}: served at {got:,} bytes, the drive's copy is {size:,}")
    return len(SOURCES)


if __name__ == "__main__":
    print(f"release assets checked: {releases()}")
    print(f"source mosaics checked: {sources()}")
    for f in fails:
        print("FAIL", f)
    print("ALL CHECKS PASS" if not fails else f"{len(fails)} FAILED")
    sys.exit(1 if fails else 0)
