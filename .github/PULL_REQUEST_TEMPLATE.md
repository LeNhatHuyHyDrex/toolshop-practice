## What this PR does

## Author checklist
- [ ] No hard-coded URL (BASE_URL / API_URL only)
- [ ] No time.sleep() / wait_for_timeout()
- [ ] Locators only in pages/, assertions only in tests/
- [ ] Test names test_<feature>_<scenario>_<expected> with a 3-line docstring
- [ ] Green locally with pytest -n auto

## Reviewer checklist
- [ ] I read every assertion: would it catch a wrong value, not just a missing element?
- [ ] Nothing depends on absolute counts or ids (PROD and BUGGY hold different data)

## CI run
