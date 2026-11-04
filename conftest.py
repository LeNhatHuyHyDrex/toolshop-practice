"""Shared fixtures for the Toolshop practice repo.

- URLs come from BASE_URL and API_URL (never hard-coded in tests).
- data-test is the test id attribute on Toolshop.
- One fresh account per session (per xdist worker), created through the API.
- Works on PROD and on BUGGY: the BUGGY API still uses the old register schema.
"""
import os
import re
import secrets
import string
import uuid
from pathlib import Path

import pytest
from playwright.sync_api import APIRequestContext, Playwright, expect

from pages.base_page import BasePage

def _load_dotenv(path: Path = Path(__file__).with_name(".env")) -> None:
    """Read KEY=VALUE lines from .env. Variables already set in the shell win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name, "").rstrip("/")
    if not value:
        raise pytest.UsageError(f"{name} is not set. Copy .env.example to .env (or export {name}=...).")
    return value


@pytest.fixture(scope="session")
def base_url() -> str:
    # No URL in code: it comes from the environment or from .env (spec: never hard-code URLs).
    return _require_env("BASE_URL")


@pytest.fixture(scope="session")
def api_url() -> str:
    return _require_env("API_URL")


@pytest.fixture(scope="session", autouse=True)
def configure_playwright(playwright: Playwright):
    playwright.selectors.set_test_id_attribute("data-test")
    # Public shared site, sometimes slow. 15 s is an upper limit for waiting, not a sleep.
    expect.set_options(timeout=15_000)
    # BUGGY uses hash routing: export ROUTE_PREFIX=/# when BASE_URL points to BUGGY.
    BasePage.route_prefix = os.getenv("ROUTE_PREFIX", "")


@pytest.fixture(scope="session")
def api(playwright: Playwright, api_url: str) -> APIRequestContext:
    context = playwright.request.new_context(
        base_url=api_url,
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def github(playwright: Playwright) -> APIRequestContext:
    """GitHub REST API client (buoi 2, syllabus 6.2).

    Without a token GitHub allows 60 requests per hour per IP address: a whole class behind one
    network uses that up in minutes. Put a personal token in .env as GITHUB_TOKEN (5000 per hour).
    """
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    context = playwright.request.new_context(base_url=_require_env("GITHUB_API_URL"), extra_http_headers=headers)
    yield context
    context.dispose()


def strong_password() -> str:
    """Toolshop rejects passwords found in data leaks, so never use welcome01 for new accounts."""
    alphabet = string.ascii_letters + string.digits
    return "Qa!" + "".join(secrets.choice(alphabet) for _ in range(10)) + "1a"


def new_email() -> str:
    return f"qa-{uuid.uuid4().hex[:12]}@example.com"


def register_user(api: APIRequestContext, email: str, password: str):
    """Register a user on PROD (address object) or BUGGY (old flat schema). Returns the response."""
    payload = {
        "first_name": "QA",
        "last_name": "Bot",
        "address": {"street": "1 Test St", "city": "Hanoi", "state": "HN",
                    "country": "VN", "postal_code": "100000"},
        "phone": "0123456789",
        "dob": "1995-01-01",
        "password": password,
        "email": email,
    }
    response = api.post("/users/register", data=payload)
    if response.status == 422 and "address" in response.json():
        legacy = {**payload, "address": "1 Test St", "city": "Hanoi", "state": "HN",
                  "country": "VN", "postcode": "100000"}
        response = api.post("/users/register", data=legacy)
    return response


@pytest.fixture(scope="session")
def test_user(api: APIRequestContext) -> dict:
    email, password = new_email(), strong_password()
    response = register_user(api, email, password)
    assert response.status == 201, f"register failed: {response.status} {response.text()}"
    return {"email": email, "password": password, "id": response.json()["id"]}


@pytest.fixture(scope="session")
def auth_token(api: APIRequestContext, test_user: dict) -> str:
    response = api.post("/users/login", data={"email": test_user["email"], "password": test_user["password"]})
    assert response.status == 200, response.text()
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def auth_state(browser, base_url: str, test_user: dict, tmp_path_factory) -> str:
    """Log in through the UI once per session and save cookies + localStorage to a file."""
    path = tmp_path_factory.mktemp("auth") / "state.json"
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.goto(BasePage.route_prefix + "/auth/login")
    page.get_by_test_id("email").fill(test_user["email"])
    page.get_by_test_id("password").fill(test_user["password"])
    page.get_by_test_id("login-submit").click()
    expect(page).to_have_url(re.compile(r"/account$"))
    context.storage_state(path=str(path))
    context.close()
    return str(path)


@pytest.fixture
def logged_in_page(new_context, auth_state: str):
    """A page in its own fresh context, already logged in (pytest-playwright tracing still applies)."""
    context = new_context(storage_state=auth_state)
    return context.new_page()
