# Bài đọc buổi 2 - API Toolshop và GitHub, chặn và giả lập mạng, chạy song song

Đọc sau buổi học ngày 11/11. Thời gian đọc khoảng 30 phút. Mọi đoạn code đã chạy thật trên Toolshop.

Sau bài này, em làm được:

1. Viết test API bằng `APIRequestContext`: kiểm mã trạng thái, cấu trúc JSON, lỗi 4xx, gọi API có token.
2. Dùng API để chuẩn bị dữ liệu và trạng thái cho test giao diện.
3. Dùng `page.route()` để chặn, giả lập và sửa phản hồi mạng.
4. Chạy song song bằng pytest-xdist và hiểu nó ảnh hưởng gì tới fixture.
5. Kiểm thử một API công khai thật (GitHub) có giới hạn lượt gọi.

## 1. Khi nào kiểm thử qua API

```
        /\        Giao diện: điều người dùng thấy và bấm. Ít, chọn lọc.
       /  \
      /----\      API: logic, mã lỗi, phân quyền, dữ liệu. Nhiều hơn, ổn định hơn.
     /      \
    /--------\    Đơn vị: phần của lập trình viên.
```

Test API kiểm được logic mà không phụ thuộc giao diện, nên ít vỡ vặt. API còn là cách nhanh để chuẩn bị dữ liệu cho test giao diện: tạo tài khoản, tạo giỏ hàng.

**Đo, đừng đoán.** Trên hệ thống nội bộ, test API thường nhanh hơn test giao diện nhiều lần. Trên Toolshop thì không hẳn. Ngày 02/11/2026, cùng kiểm tra "giỏ có 2 sản phẩm", test giao diện mất khoảng 6 giây, còn test API mất khoảng 7 giây, vì API công cộng của Toolshop trả chậm. Muốn biết test nào chậm, chạy `pytest --durations=5`.

## 2. APIRequestContext

Playwright có sẵn một HTTP client. Đề đồ án yêu cầu dùng nó, không dùng thư viện `requests`, để cả giao diện và API đi chung một framework.

Fixture `api` trong `conftest.py`:

```python
@pytest.fixture(scope="session")
def api(playwright, api_url):
    context = playwright.request.new_context(
        base_url=api_url,                                  # lấy từ API_URL, không viết cứng
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()
```

Những gì hay dùng trên một phản hồi:

| Thuộc tính, hàm | Trả về |
|---|---|
| `response.status` | Mã trạng thái, ví dụ `201` |
| `response.ok` | `True` với mọi mã 2xx |
| `response.json()` | Thân phản hồi dạng dict hoặc list |
| `response.text()` | Thân phản hồi dạng chuỗi, nên in ra khi assert đỏ |

Test API đầu tiên:

```python
@pytest.mark.api
def test_status_returns_toolshop(api):
    """Goal: API is alive. Precondition: none. Expected: 200 and app_name Toolshop."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"
```

`response.text()` ở cuối dòng assert là thông báo lỗi: khi đỏ, em thấy luôn server trả về gì.

Mọi endpoint của Toolshop có trong Swagger: https://api.practicesoftwaretesting.com/api/documentation

## 3. Viết assertion cho API

### 3.1 Kiểm mã cụ thể

`assert response.ok` chấp nhận cả 200, 201, 204. Khi biết rõ tạo mới phải trả 201, hãy kiểm `== 201`. Assertion càng cụ thể càng bắt được nhiều lỗi.

### 3.2 Kiểm cấu trúc, không kiểm con số

PROD và BUGGY là hai môi trường có dữ liệu khác nhau:

| | PROD | BUGGY |
|---|---|---|
| Số sản phẩm | 50 | 26 |
| Kiểu id | chuỗi, ví dụ `01M66...` | số nguyên, ví dụ `1` |

Site lại dùng chung với nhiều người, nên dữ liệu còn thay đổi theo ngày. Kiểm hành vi và cấu trúc:

```python
def test_products_first_page_has_pagination_and_product_shape(api):
    """Goal: contract of GET /products. Precondition: none.
    Expected: pagination keys, non-empty data, id/name/price with sane types."""
    body = api.get("/products", params={"page": 1}).json()
    for key in ("current_page", "data", "per_page", "total", "last_page"):
        assert key in body, f"missing key {key}"
    assert 0 < len(body["data"]) <= body["per_page"]
    for product in body["data"]:
        assert isinstance(product["id"], (str, int))
        assert isinstance(product["name"], str) and product["name"].strip()
        assert isinstance(product["price"], (int, float)) and product["price"] > 0
```

Không có dòng nào viết `total == 50`.

### 3.3 Lỗi 4xx bằng parametrize

```python
@pytest.mark.parametrize("path, expected", [("/users/me", 401), ("/products/does-not-exist", 404)])
def test_protected_or_missing_resource_returns_4xx(api, path, expected):
    assert api.get(path).status == expected
```

Một hàm, hai test. Gửi form đăng ký rỗng thì Toolshop trả 422 kèm danh sách lỗi theo từng trường (`email`, `password`, ...).

## 4. Đăng ký, đăng nhập, token

Repo có sẵn chuỗi fixture:

| Fixture | Phạm vi | Làm gì |
|---|---|---|
| `test_user` | session | Tạo tài khoản mới qua `POST /users/register`, email chứa chuỗi ngẫu nhiên |
| `auth_token` | session | `POST /users/login` bằng tài khoản đó, lấy `access_token` |
| `auth_headers` | session | `{"Authorization": "Bearer <token>"}` |

Dùng trong test:

```python
def test_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]
```

Hai điều về dữ liệu đăng ký:

- **Mật khẩu phổ biến bị từ chối.** Toolshop chặn mật khẩu từng xuất hiện trong các vụ lộ dữ liệu. `welcome01` hay `Welcome01!` nhận 422 "The given password has appeared in a data leak". Fixture dùng `strong_password()` để sinh mật khẩu ngẫu nhiên.
- **Mỗi nhóm dùng tài khoản riêng cho test có ghi dữ liệu.** Tài khoản mẫu `customer@...` cả lớp dùng chung, chỉ để đọc.

### Phạm vi (scope) của fixture

| Scope | Tạo lại khi nào | Dùng cho |
|---|---|---|
| `function` (mặc định) | Mỗi test | Thứ cần cách ly: page, context, giỏ hàng |
| `module` | Mỗi file test | Ít dùng trong đồ án |
| `session` | Một lần cho cả phiên chạy | Thứ đắt và chỉ đọc: API context, tài khoản, token |

Tự viết fixture của mình, ví dụ một giỏ hàng mới cho mỗi test:

```python
@pytest.fixture
def new_cart(api):
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]
```

## 5. Data-driven: đọc dữ liệu từ file

```python
KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text())

@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_search_api_returns_only_matching_names(api, case):
    body = api.get("/products/search", params={"q": case["keyword"]}).json()
    names = [p["name"] for p in body["data"]]
    assert names, f"no results for {case['keyword']}"
    assert all(case["must_contain"] in n.lower() for n in names), names
```

Thêm một dòng vào `data/search_keywords.json` là có thêm một test, không sửa code. `ids=` đặt tên dễ đọc cho từng test trong báo cáo.

## 6. Chặn và giả lập mạng với `page.route()`

### 6.1 Ba cách can thiệp một request

```python
# Chặn: trang vẫn dùng được khi không có ảnh (và tải nhanh hơn)
page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), lambda route: route.abort())

# Giả lập: trả về phản hồi tự viết
page.route(PRODUCT_LIST, lambda route: route.fulfill(
    status=200, content_type="application/json", body=json.dumps(EMPTY_PAGE)))

# Sửa phản hồi thật
def patch(route):
    response = route.fetch()          # gọi server thật
    body = response.json()
    body["data"][0]["price"] = 999.99
    route.fulfill(response=response, json=body)
page.route(PRODUCT_LIST, patch)
```

Luôn đăng ký route **trước** khi mở trang. Đăng ký sau thì request đã đi mất.

### 6.2 Xem request thật trước khi viết pattern

Mở trang chủ, F12, tab Network, lọc `products`:

| Môi trường | Request tải danh sách sản phẩm |
|---|---|
| PROD | `QUERY /products`, điều kiện nằm trong body JSON |
| BUGGY | `GET /products?between=price,1&page=1` |

QUERY là một phương thức HTTP mới, gửi điều kiện tìm trong body thay vì trên URL. Glob `**/products?*` không bắt được request QUERY của PROD vì URL không có dấu `?`. Repo dùng regex bắt cả hai:

```python
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
```

Dấu `$` ở cuối giúp regex không bắt nhầm `/products/search` hay `/products/{id}`.

### 6.3 Test phải chứng minh điều kiện của chính nó

Test chặn ảnh chỉ kiểm "sản phẩm vẫn hiện" thì vẫn xanh khi route viết sai và không chặn gì. Ghi lại URL bị chặn, rồi kiểm danh sách đó không rỗng:

```python
blocked = []
def block(route):
    blocked.append(route.request.url)
    route.abort()
page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block)
home = HomePage(page).open()
expect(home.product_names.first).to_be_visible()
assert blocked, "no image request was blocked"
```

Nguyên tắc: mock để tạo tình huống khó tạo bằng dữ liệu thật (danh sách rỗng, lỗi 500), không mock để test xanh.

## 7. API giúp test giao diện

### 7.1 Browser, context, page

| | Là gì | Ví dụ |
|---|---|---|
| Browser | Một tiến trình trình duyệt | Chromium |
| Context | Một phiên độc lập: cookie, localStorage riêng, giống cửa sổ ẩn danh | Mỗi test một context |
| Page | Một tab trong context | Trang Toolshop đang mở |

Tạo context chỉ mất vài mili giây, nên mỗi test một context: test này không để lại giỏ hàng hay phiên đăng nhập cho test khác.

### 7.2 Đăng nhập một lần, dùng lại nhiều lần

Fixture `auth_state` đăng nhập qua giao diện một lần mỗi phiên rồi lưu cookie và localStorage vào file. Fixture `logged_in_page` mở context mới từ file đó cho từng test:

```python
@pytest.fixture
def logged_in_page(new_context, auth_state):
    context = new_context(storage_state=auth_state)
    return context.new_page()
```

Được: tiết kiệm một lần đăng nhập cho mỗi test. Rủi ro: token có thể hết hạn giữa chừng, và file trạng thái chứa token không được commit.

### 7.3 Bỏ qua form đăng nhập bằng token

Toolshop PROD giữ token trong localStorage, khoá `auth-token`. `add_init_script` chạy trước mã của trang, nên token có sẵn khi Toolshop khởi động:

```python
token = json.dumps(auth_token)
page.add_init_script(f"localStorage.setItem('auth-token', {token})")
account = AccountPage(page).open()
expect(account.title).to_have_text("My account")
```

## 8. Chạy song song

```bash
pytest -n auto                 # máy cá nhân: một worker cho mỗi nhân CPU
pytest -n 4 --durations=5      # so thời gian với chạy tuần tự
```

Mỗi worker của pytest-xdist là một phiên pytest riêng. Vì vậy fixture `scope="session"` chạy **một lần cho mỗi worker**: `-n 4` tạo 4 tài khoản `test_user`. Email phải duy nhất, nếu không thì lần đăng ký thứ hai nhận 409 "A customer with this email address already exists."

Trên CI, đồ án dùng `-n 2`: máy của GitHub có 2 nhân, và Toolshop là site dùng chung, bắn quá nhiều luồng vào sẽ tự tạo ra test chập chờn.

**Tắt JavaScript không giúp gì với Toolshop.** Mở context với `java_script_enabled=False` thì trang Toolshop trắng hoàn toàn, vì nó là ứng dụng Angular dựng giao diện bằng JavaScript. Mẹo này chỉ có ích với trang dựng sẵn từ server.

## 9. Thực hành với GitHub API

Nội dung học phần có mục "Thực hành tương tác với GitHub API". Cùng `APIRequestContext`, nhưng là một API công khai thật, khác Toolshop ở ba điểm đáng học:

- **Header phiên bản.** GitHub yêu cầu `Accept: application/vnd.github+json` và khuyên gửi `X-GitHub-Api-Version`, để API đổi phiên bản không làm vỡ client cũ.
- **Thân lỗi chuẩn.** Tài nguyên không tồn tại trả 404 với `{"message": "Not Found", ...}`.
- **Giới hạn lượt gọi.** Không có token: 60 lượt mỗi giờ cho mỗi địa chỉ IP. Có token cá nhân: 5.000 lượt mỗi giờ. Mọi phản hồi đều kèm header `x-ratelimit-limit`, `x-ratelimit-remaining`. Riêng `GET /rate_limit` không bị tính lượt.

Fixture `github` trong `conftest.py`:

```python
@pytest.fixture(scope="session")
def github(playwright):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    context = playwright.request.new_context(base_url=_require_env("GITHUB_API_URL"), extra_http_headers=headers)
    yield context
    context.dispose()
```

Ví dụ kiểm thông tin một repo:

```python
def test_github_repo_returns_expected_metadata(github):
    response = github.get("/repos/microsoft/playwright-python")
    assert response.status == 200, response.text()
    repo = response.json()
    assert repo["full_name"] == "microsoft/playwright-python"
    assert repo["license"]["spdx_id"] == "Apache-2.0"
    assert isinstance(repo["stargazers_count"], int) and repo["stargazers_count"] > 0
```

Số sao thay đổi mỗi ngày, nên test kiểm kiểu và dấu, không kiểm con số. Đây cùng nguyên tắc với dữ liệu Toolshop.

**Tạo token:** github.com, Settings, Developer settings, Fine-grained tokens, Generate new token. Đọc dữ liệu công khai thì không cần chọn quyền nào. Điền vào dòng `GITHUB_TOKEN=` trong `.env`. Token là mật khẩu: không commit, không dán vào chat hay AI. Lỡ lộ thì xoá token trên GitHub ngay.

Khi hết lượt, GitHub trả 403 hoặc 429 với thông báo có chữ "rate limit exceeded". Test đỏ vì lý do này không phải lỗi của test: đó là giới hạn của hệ thống bên ngoài. Trên GitHub Actions, workflow có sẵn một token tự động (`secrets.GITHUB_TOKEN`), đồ án đã cấu hình trong `ci.yml`.

## 10. Lỗi thường gặp

| Triệu chứng | Nguyên nhân |
|---|---|
| Đăng ký nhận 422 "appeared in a data leak" | Mật khẩu phổ biến |
| Đăng ký nhận 409 "A customer with this email address already exists." | Email cố định, hoặc chạy song song với email không ngẫu nhiên |
| Route không có tác dụng | Đăng ký sau `goto`, hoặc pattern không khớp request QUERY |
| Mock rỗng làm hỏng cả ô tìm kiếm | Pattern quá rộng, bắt cả `/products/search` |
| `TypeError` khi fulfill | Truyền dict vào `body=`. Dùng `json.dumps(...)` hoặc tham số `json=` |
| Bị trừ điểm hard-code URL | Viết `https://...` trong test thay vì dùng `base_url`, `api_url` |
| GitHub trả 403 hoặc 429 "rate limit exceeded" | Hết lượt gọi của IP. Thêm `GITHUB_TOKEN` vào `.env` |
| `KeyError` khi đọc header | Khoá header trong Playwright viết thường: `x-ratelimit-remaining` |

## 11. Tự kiểm tra

1. `assert response.ok` và `assert response.status == 201` khác nhau thế nào? Khi nào dùng cái nào?
2. Vì sao test API của nhóm không nên kiểm `total == 50`?
3. Chạy `pytest -n 4`, fixture `test_user` chạy mấy lần? Vì sao?
4. Vì sao route phải đăng ký trước khi mở trang?
5. `storage_state` tiết kiệm được gì, và có rủi ro gì?
6. Kể hai tình huống nên kiểm thử qua API thay vì qua giao diện.
7. Vì sao test GitHub không kiểm `stargazers_count == 15084`? Nếu test đỏ vì "rate limit exceeded", đó là lỗi của ai?

## 12. Liên hệ đồ án

- Mục 3.3 Data-driven, 3.4 Fixture và marker, 3.5 Test API, 3.6 Route và mocking, 3.11 chạy song song. Nội dung học phần 6.1 đến 6.4.
- Câu vấn đáp 3, 4, 8, 10, 14.

## 13. Đọc thêm

- API testing: https://playwright.dev/python/docs/api-testing
- GitHub REST API: https://docs.github.com/en/rest
- Giới hạn lượt gọi của GitHub: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- Network, route: https://playwright.dev/python/docs/network
- pytest-xdist: https://pytest-xdist.readthedocs.io/
- Fixture của pytest: https://docs.pytest.org/en/stable/how-to/fixtures.html
