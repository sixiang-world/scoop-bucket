#!/usr/bin/env python3
"""
Scoop Bucket 自动更新脚本
定期检查上游 GitHub Release，有新版本时自动更新 manifest。

用法:
    python scripts/update-warp-cn.py         # 检查并更新 warp-cn
    python scripts/update-warp-cn.py --dry   # 只检查，不写入
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.request

# ── 配置 ──────────────────────────────────────────────
MANIFEST_PATH = "bucket/warp-cn.json"
REPO = "Heartcoolman/warp-cn"
ASSET_NAME = "WarpOssSetup.exe"  # Windows 安装包

DRY_RUN = "--dry" in sys.argv

# ── GitHub API ────────────────────────────────────────


def api_get(url):
    """GET GitHub API, 携带 token 避免限流"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "scoop-bucket-updater/1.0",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get_latest_release():
    """获取最新 release 信息"""
    data = api_get(f"https://api.github.com/repos/{REPO}/releases/latest")
    tag = data["tag_name"]  # e.g. "v0.2026.06.09-cn.0"
    version = tag.lstrip("v")

    # 找到 Windows 的 exe asset
    exe_asset = None
    for asset in data["assets"]:
        if asset["name"] == ASSET_NAME:
            exe_asset = asset
            break

    if not exe_asset:
        print(f"::error::No asset named '{ASSET_NAME}' found in latest release")
        sys.exit(1)

    return tag, version, exe_asset["browser_download_url"]


def compute_sha256(url):
    """下载文件并计算 SHA256"""
    print(f"  Downloading: {url}")
    sha256 = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": "scoop-bucket-updater/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def read_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
        f.write("\n")  # trailing newline


def update_manifest(new_version, new_hash, new_url):
    """更新 manifest 中的版本、hash 和 URL"""
    manifest = read_manifest()
    old_version = manifest.get("version", "(none)")

    if new_version == old_version:
        print(f"  No update needed (current: {old_version})")
        return False

    print(f"  Updating: {old_version} → {new_version}")

    manifest["version"] = new_version
    manifest["architecture"]["64bit"]["url"] = new_url
    manifest["architecture"]["64bit"]["hash"] = new_hash

    if DRY_RUN:
        print("  [DRY RUN] Would write manifest:")
        print(json.dumps(manifest, indent=4, ensure_ascii=False))
    else:
        write_manifest(manifest)
        print(f"  Written: {MANIFEST_PATH}")

    return True


def main():
    print(f"=== Checking {REPO} ===")

    tag, version, url = get_latest_release()
    print(f"  Latest tag: {tag}")
    print(f"  Latest version: {version}")

    manifest = read_manifest()
    current_version = manifest.get("version", "0.0.0")
    print(f"  Current manifest version: {current_version}")

    # 版本比较（简洁的字符串比较，因为格式固定为 0.YYYY.MM.DD-cn.N）
    if version == current_version:
        print("  ✓ Already up-to-date")
        return

    hash_value = compute_sha256(url)
    print(f"  SHA256: {hash_value}")

    updated = update_manifest(version, hash_value, url)
    if updated:
        # 设置 GitHub Actions 输出
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"updated=true\n")
                f.write(f"new_version={version}\n")
                f.write(f"old_version={current_version}\n")
        print("  ✓ Manifest updated")


if __name__ == "__main__":
    main()
