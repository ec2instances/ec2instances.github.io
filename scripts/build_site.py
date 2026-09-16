"""Build a self-contained Pages site with a validated snapshot of AWS pricing."""

import gzip
import json
import math
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
BASE_URL = "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel"


def fetch_json(path):
    url = f"{BASE_URL}/{path}"
    for attempt in range(3):
        try:
            request = Request(url, headers={"Accept-Encoding": "gzip"})
            with urlopen(request, timeout=60) as response:
                body = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return json.loads(body)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")


def download_region(region):
    instances = []
    for os_name in ("Linux", "Windows"):
        data = fetch_json(f"{quote(region, safe='')}/{os_name}/index.json")
        rows = data["regions"][region]
        if not isinstance(rows, dict) or not rows:
            raise ValueError(f"Empty or invalid pricing for {region}/{os_name}")
        for row in rows.values():
            if not row.get("Instance Type") or row.get("Operating System") != os_name:
                raise ValueError(f"Invalid instance in {region}/{os_name}")
            price = float(row["price"])
            if not row.get("Memory") or not math.isfinite(price) or price < 0:
                raise ValueError(f"Invalid memory or price in {region}/{os_name}")
        instances.extend(rows.values())
    write_json(OUTPUT / "data" / f"{region}.json", instances)
    print(f"{region}: {len(instances)} prices", flush=True)


def main():
    metadata = fetch_json("metadata.json")
    regions = metadata["regionAttributes"]["Location"]
    if not isinstance(regions, list) or not regions:
        raise ValueError("AWS returned no regions")
    if any(not isinstance(r, str) or not r or "/" in r or "\\" in r for r in regions):
        raise ValueError("Invalid region names")
    # A clean build prevents removed regions from lingering in future deployments.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(download_region, sorted(set(regions))))
    write_json(OUTPUT / "data" / "metadata.json", {
        "regions": sorted(set(regions)),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    })
    shutil.copy2(ROOT / "index.html", OUTPUT / "index.html")
    if (ROOT / "CNAME").exists():
        shutil.copy2(ROOT / "CNAME", OUTPUT / "CNAME")
    print(f"Built {len(set(regions))} regions in {OUTPUT}")


if __name__ == "__main__":
    main()
