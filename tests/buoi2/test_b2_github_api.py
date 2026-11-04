"""Buoi 2 - B2.13 GitHub REST API (syllabus 6.2).

Same APIRequestContext you used for Toolshop, on a different, real public API.
Fixture: github (see conftest.py). Docs: https://docs.github.com/en/rest

Rate limit: without a token GitHub allows 60 calls per hour per IP address. The whole class shares
the school's IP, so create a token (github.com > Settings > Developer settings > Fine-grained tokens,
no permissions needed) and put it in .env as GITHUB_TOKEN. Never commit .env.

Run:  pytest tests/buoi2/test_b2_github_api.py -v
"""
import uuid  # noqa: F401  (you will need it)

import pytest

pytestmark = [pytest.mark.api, pytest.mark.github]

REPO = "microsoft/playwright-python"


# ---------------------------------------------------------------- B2.13a
def test_b2_13a_github_repo_returns_expected_metadata(github):
    """Goal: GET /repos/{owner}/{repo} describes the repository.
    Precondition: the repository is public.
    Expected: 200, full_name equals REPO, language Python, licence spdx_id Apache-2.0,
    stargazers_count is an int > 0, archived is False."""
    raise NotImplementedError("B2.13a")


# ---------------------------------------------------------------- B2.13b
def test_b2_13b_github_unknown_user_returns_404_with_message(github):
    """Goal: GitHub explains missing resources.
    Precondition: a login that cannot exist (use uuid).
    Expected: 404 and the JSON message 'Not Found'."""
    raise NotImplementedError("B2.13b")


# ---------------------------------------------------------------- B2.13c
def test_b2_13c_github_response_reports_rate_limit(github):
    """Goal: responses carry rate-limit headers.
    Precondition: none. Use GET /rate_limit: it does not count against your limit.
    Expected: headers x-ratelimit-limit and x-ratelimit-remaining are integers and remaining <= limit.
    Hint: response.headers is a dict with lower-case keys."""
    raise NotImplementedError("B2.13c")


# ---------------------------------------------------------------- B2.13d (challenge)
def test_b2_13d_github_latest_release_matches_installed_playwright(github):
    """Goal: connect an API answer to something you can check locally.
    Precondition: playwright installed from requirements.txt.
    Expected: GET /repos/{REPO}/releases/latest has tag_name like v1.64.1, not older than
    importlib.metadata.version("playwright")."""
    raise NotImplementedError("B2.13d")
