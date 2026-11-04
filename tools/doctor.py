"""Kiểm tra máy trước buổi học. Chạy từ thư mục gốc của repo, trong môi trường ảo đã kích hoạt:

    python tools/doctor.py

Mỗi dòng in [OK], [LỖI] hoặc [LƯU Ý] kèm cách sửa. Có [LỖI] thì lệnh trả mã thoát 1.
Chạy được trên Windows, macOS và Linux. Không ghi gì vào máy, không gửi dữ liệu đi đâu.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
results: list[tuple[str, str, str]] = []  # (status, title, hint)


def ok(title: str, hint: str = "") -> None:
    results.append(("OK", title, hint))


def error(title: str, hint: str) -> None:
    results.append(("LỖI", title, hint))


def warn(title: str, hint: str) -> None:
    results.append(("LƯU Ý", title, hint))


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    for key in ("BASE_URL", "API_URL", "ROUTE_PREFIX", "GITHUB_API_URL", "GITHUB_TOKEN"):
        if os.getenv(key):
            values[key] = os.environ[key]  # shell wins over .env, same rule as conftest.py
    return values


def get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 20):
    request = urllib.request.Request(url, headers={"Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8")), response.headers


def check_python() -> None:
    v = sys.version_info
    label = f"Python {v.major}.{v.minor}.{v.micro}"
    if v < (3, 10):
        error(label, "Cần Python 3.10 trở lên, khuyến nghị 3.12: https://www.python.org/downloads/")
    elif (v.major, v.minor) != (3, 12):
        warn(label, "Chạy được, nhưng lớp dùng 3.12. Gặp lỗi lạ thì cài 3.12 cho giống lớp.")
    else:
        ok(label)
    if sys.prefix == sys.base_prefix:
        warn("Chưa ở trong môi trường ảo (.venv)",
             "Windows: .venv\\Scripts\\activate    macOS/Linux: source .venv/bin/activate")
    else:
        ok("Đang dùng môi trường ảo")


def check_packages() -> None:
    req = ROOT / "requirements.txt"
    if not req.exists():
        error("Không thấy requirements.txt", "Chạy lệnh này từ thư mục gốc của repo.")
        return
    missing, different = [], []
    for line in req.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line or "==" not in line:
            continue
        name, wanted = line.split("==", 1)
        try:
            have = metadata.version(name)
        except metadata.PackageNotFoundError:
            missing.append(name)
            continue
        if have != wanted:
            different.append(f"{name} {have} (lớp dùng {wanted})")
    if missing:
        error("Thiếu thư viện: " + ", ".join(missing), "pip install -r requirements.txt")
    else:
        ok("Đủ thư viện trong requirements.txt")
    if different:
        warn("Khác phiên bản: " + "; ".join(different), "pip install -r requirements.txt để giống cả lớp")


def check_env(env: dict[str, str]) -> None:
    if not (ROOT / ".env").exists():
        error("Chưa có tệp .env", "Windows: copy .env.example .env    macOS/Linux: cp .env.example .env")
    for key in ("BASE_URL", "API_URL"):
        if env.get(key):
            ok(f"{key} = {env[key]}")
        else:
            error(f"Thiếu {key}", "Mở .env và điền theo .env.example")
    if "with-bugs" in env.get("BASE_URL", "") and env.get("ROUTE_PREFIX") != "/#":
        error("Đang trỏ BUGGY nhưng ROUTE_PREFIX chưa là /#", "BUGGY dùng đường dẫn /#/..., đặt ROUTE_PREFIX=/#")
    if not env.get("GITHUB_API_URL"):
        warn("Thiếu GITHUB_API_URL (bài GitHub API buổi 2)", "Thêm dòng GITHUB_API_URL=https://api.github.com vào .env")


def check_toolshop(env: dict[str, str]) -> None:
    api = env.get("API_URL", "").rstrip("/")
    if not api:
        return
    try:
        status, body, _ = get_json(api + "/status")
        if status == 200 and body.get("app_name") == "Toolshop":
            ok(f"API Toolshop trả lời ({body.get('version', '?')})")
        else:
            error(f"API Toolshop trả {status}", "Thử lại sau vài phút. Site công cộng có thể đang chậm.")
    except Exception as exc:  # noqa: BLE001 - show any network problem in plain words
        error(f"Không gọi được {api}/status ({type(exc).__name__})",
              "Kiểm tra mạng, proxy của trường, hoặc site đang sập. Mở địa chỉ đó bằng trình duyệt thử.")


def check_browser(env: dict[str, str]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        error("Chưa cài Playwright cho Python", "pip install -r requirements.txt")
        return
    base = env.get("BASE_URL", "").rstrip("/")
    try:
        with sync_playwright() as p:
            p.selectors.set_test_id_attribute("data-test")
            browser = p.chromium.launch()
            ok(f"Chromium mở được (phiên bản {browser.version})")
            if base:
                page = browser.new_page()
                page.goto(base + env.get("ROUTE_PREFIX", "") + "/", timeout=30_000)
                page.get_by_test_id("product-name").first.wait_for(timeout=30_000)
                count = page.get_by_test_id("product-name").count()
                ok(f"Trang chủ Toolshop hiện {count} sản phẩm")
            browser.close()
    except Exception as exc:  # noqa: BLE001
        text = str(exc)
        if "Executable doesn't exist" in text or "playwright install" in text:
            error("Chưa tải trình duyệt cho Playwright", "playwright install chromium")
        else:
            error(f"Không mở được Toolshop bằng Chromium ({type(exc).__name__})", text.splitlines()[0][:160])


def check_github(env: dict[str, str]) -> None:
    url = env.get("GITHUB_API_URL", "").rstrip("/")
    if not url:
        return
    headers = {"Accept": "application/vnd.github+json"}
    token = env.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        _, body, _ = get_json(url + "/rate_limit", headers)  # this call does not use up the limit
        core = body["resources"]["core"]
        line = f"GitHub API: còn {core['remaining']}/{core['limit']} lượt gọi trong giờ này"
        if token and core["limit"] >= 5000:
            ok(line + " (đã dùng token)")
        elif token:
            warn(line, "Token có vẻ không hợp lệ, kiểm tra lại GITHUB_TOKEN trong .env")
        elif core["remaining"] < 20:
            warn(line, "Sắp hết lượt. Tạo token: github.com > Settings > Developer settings > Fine-grained tokens")
        else:
            warn(line + " (chưa có token)", "Cả lớp chung một IP chỉ có 60 lượt/giờ. Nên tạo token cho buổi 2.")
    except Exception as exc:  # noqa: BLE001
        warn(f"Không gọi được GitHub API ({type(exc).__name__})", "Chỉ cần cho bài GitHub API buổi 2.")


def run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def check_tools() -> None:
    if shutil.which("git"):
        name, email = run(["git", "config", "user.name"]), run(["git", "config", "user.email"])
        if name and email:
            ok(f"Git: {run(['git', '--version'])}, tên '{name}'")
        else:
            warn("Git chưa đặt tên, email",
                 'git config --global user.name "Ten Cua Em"  và  git config --global user.email em@example.com')
    else:
        error("Chưa cài Git", "https://git-scm.com/downloads")
    if shutil.which("npx") or shutil.which("npx.cmd"):
        ok(f"Node.js {run(['node', '--version'])} (cần cho Playwright MCP, buổi 4)")
    else:
        warn("Chưa có Node.js (chỉ cần cho bài AI buổi 4)", "Cài bản LTS: https://nodejs.org/")


def main() -> int:
    # Old Windows consoles default to a legacy code page: keep Vietnamese text printable everywhere.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    print(f"Kiểm tra máy cho lớp Automation Testing ({platform.system()} {platform.release()})\n")
    env = read_env()
    check_python()
    check_packages()
    check_env(env)
    check_toolshop(env)
    check_browser(env)
    check_github(env)
    check_tools()
    width = max(len(s) for s, _, _ in results) + 2
    for status, title, hint in results:
        print(f"[{status}]".ljust(width + 1) + title)
        if hint and status != "OK":
            print(" " * (width + 1) + "-> " + hint)
    errors = sum(1 for s, _, _ in results if s == "LỖI")
    warnings = sum(1 for s, _, _ in results if s == "LƯU Ý")
    print(f"\n{errors} lỗi, {warnings} lưu ý. " + ("Máy đã sẵn sàng." if errors == 0 else "Sửa các dòng [LỖI] rồi chạy lại."))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
