# Bài đọc buổi 4 - Test chập chờn, gỡ lỗi, săn lỗi trên BUGGY, AI

Đọc sau buổi học ngày 25/11, trước khi làm Sprint 3 và chuẩn bị vấn đáp. Thời gian đọc khoảng 35 phút.

Sau bài này, em làm được:

1. Nhận ra 5 nguyên nhân phổ biến của test chập chờn (flaky) và chữa không cần `sleep`.
2. Gỡ lỗi theo trình tự bằng trace, chế độ có giao diện, và Inspector.
3. Chạy bộ test trên BUGGY, phân loại từng test đỏ, viết báo cáo lỗi đạt chuẩn.
4. Dùng AI để viết test và biết phải soát những gì.

## 1. Test chập chờn là gì

Test chập chờn (flaky) là test lúc xanh lúc đỏ dù code không đổi. Nó nguy hiểm hơn test đỏ hẳn: dần dần cả nhóm quen "đỏ thì chạy lại", và đến khi có lỗi thật thì không ai tin CI nữa.

### 1.1 Năm nguyên nhân phổ biến

| Nguyên nhân | Dấu hiệu | Cách chữa |
|---|---|---|
| Đọc trang trước khi nó cập nhật | Đọc ra dữ liệu cũ. Chạy từng bước thì xanh | Chờ đúng điều kiện bằng `expect(...)` hoặc chờ phản hồi mạng |
| Chờ theo đồng hồ | Có `sleep`. Xanh trên máy nhanh, đỏ trên CI | Bỏ `sleep`, chờ sự kiện |
| Phụ thuộc thứ tự | Chạy cả file thì xanh, chạy riêng thì đỏ | Mỗi test tự chuẩn bị dữ liệu bằng fixture |
| Dữ liệu cố định, dùng lại | Lần đầu xanh, các lần sau đỏ | Dữ liệu duy nhất mỗi lần chạy: email có uuid |
| Bất đồng bộ chồng nhau | Nhiều request, phản hồi về lộn thứ tự. Chạy song song thì đỏ nhiều hơn | Mỗi thao tác chờ phản hồi của nó, rồi chờ giao diện vẽ xong |

### 1.2 Hàm nào chờ, hàm nào không

| Không chờ, đọc ngay | Có chờ |
|---|---|
| `locator.inner_text()`, `all_inner_texts()` | `expect(locator).to_have_text(...)` |
| `locator.count()` | `expect(locator).to_have_count(n)` |
| `locator.is_visible()` | `expect(locator).to_be_visible()` |
| `assert` của Python | `click()`, `fill()`: tự chờ phần tử hiện, ổn định, bấm được |

Trước khi bấm, Playwright tự chờ phần tử: có trong DOM, hiển thị, đứng yên (không đang chuyển động), không bị che, và được bật. `expect()` thì thử lại đến khi đúng hoặc hết thời gian chờ (repo đặt 15 giây vì Toolshop là site dùng chung).

### 1.3 Công cụ chờ đúng sự kiện

```python
# Chờ phần tử báo hiệu xong mà Toolshop cung cấp
home.search("hammer")
expect(home.search_completed).to_be_visible()
names = home.product_names.all_inner_texts()      # giờ mới đọc

# Chờ phản hồi mạng của chính thao tác vừa làm
with page.expect_response(lambda r: "/products" in r.url and r.ok):
    home.sort_by("price,desc")

# Lấy dữ liệu từ phản hồi rồi chờ giao diện hiển thị đúng dữ liệu đó
with page.expect_response(lambda r: "/products" in r.url) as last:
    page.keyboard.press("PageDown")
expected = [p["name"] for p in last.value.json()["data"]]
expect(home.product_names).to_have_text(expected)
```

Cách cuối đáng nhớ: phản hồi về rồi nhưng giao diện còn cần một nhịp để vẽ lại. Chờ đúng thứ mình sắp kiểm.

### 1.4 Một chuyện có thật trên Toolshop

Khi chạy song song, test tìm kiếm đỏ khoảng 1 lần trong 3: danh sách đọc được là danh sách trang chủ, dù Toolshop đã báo tìm xong.

```
mở trang ------------------------------------------------------>
   tìm "saw" ------------------------------------------------->
   [kết quả tìm "saw" về trước, hiện Wood Saw, Circular Saw]
   [danh sách trang chủ (gửi lúc mở trang) về muộn, GHI ĐÈ kết quả]
```

Đây vừa là lỗi của ứng dụng (lẽ ra phải bỏ request cũ khi người dùng tìm), vừa là bài học cho test: phải chờ trang sẵn sàng. Cách chữa trong repo: `HomePage.open()` chờ phản hồi danh sách đầu tiên rồi mới trả về.

### 1.5 Chạy lại có chữa được flaky không

`--reruns 1` giúp chịu được một lần mạng chập chờn. Nó **che mất** race condition thật của ứng dụng, test phụ thuộc thứ tự, và dữ liệu dùng chung bị sửa. Đồ án dùng `--reruns 1` trên CI. Test nào lần nào cũng cần chạy lại thì đó là lỗi, của test hoặc của ứng dụng.

## 2. Gỡ lỗi theo trình tự

Khi một test đỏ, đi theo thứ tự:

1. **Đọc thông báo lỗi.** Lỗi assertion (sai giá trị) hay timeout (không tìm thấy, không chờ được)? Dòng `E ` cho biết locator nào, mong gì, nhận gì.
2. **Mở trace.** Trên CI: tải artifact. Ở máy: `pytest -k <tên> --tracing on`, rồi `playwright show-trace test-results/<thư-mục>/trace.zip`.
3. **Tái hiện có giao diện.** `pytest -k <tên> --headed --slowmo 500`. Test chỉ đỏ trên một trình duyệt thì thêm `--browser webkit`.
4. **Dừng tại chỗ nghi ngờ.** `PWDEBUG=1 pytest -k <tên>` mở Playwright Inspector, hoặc chèn `page.pause()` tạm thời.
5. **Chạy lại đúng các test đỏ.** `pytest --lf -x`.
6. **Phân loại.** Lỗi của test, lỗi môi trường, hay lỗi của ứng dụng. Chỉ loại cuối vào báo cáo lỗi.

Trace Viewer có:

| Phần | Cho xem |
|---|---|
| Thanh thời gian phía trên | Bước nào mất bao lâu |
| Danh sách hành động | Từng lệnh của test, lệnh đỏ được đánh dấu |
| Ảnh DOM Before, After | Trang trông thế nào trước và sau mỗi bước |
| Network | Mọi request: phương thức, URL, body, mã trạng thái |
| Console | Lỗi JavaScript của trang |

## 3. Bảy nguyên tắc viết test

1. Một test, một hành vi. Tên test nói được hành vi đó: `test_<chức_năng>_<kịch_bản>_<kết_quả>`.
2. Độc lập: chạy một mình được, đảo thứ tự được, chạy song song được.
3. Ba khối rõ ràng: chuẩn bị, hành động, kiểm tra.
4. Kiểm thứ người dùng thấy (chữ, số dòng, URL), không kiểm cấu trúc DOM.
5. Không dùng `if`, `for` để quyết định có kiểm hay không. Dữ liệu khác nhau thì dùng parametrize.
6. Dữ liệu tự tạo, duy nhất, không dùng tài khoản chung để ghi.
7. Mock để tạo tình huống khó tạo bằng dữ liệu thật, không mock để test xanh.

Các dấu hiệu test yếu: assert luôn đúng, test không có assert, `try/except` nuốt lỗi, `pytest.skip` khi dữ liệu không như mong đợi, kiểm `status in (200, 201, 204)` khi đã biết chắc là 201.

## 4. Săn lỗi trên BUGGY

### 4.1 Chạy cùng bộ test trên môi trường khác

```bash
# macOS, Linux
BASE_URL=https://with-bugs.practicesoftwaretesting.com \
API_URL=https://api-with-bugs.practicesoftwaretesting.com \
ROUTE_PREFIX=/# \
pytest --tracing retain-on-failure --screenshot only-on-failure
```

```powershell
# Windows PowerShell
$env:BASE_URL="https://with-bugs.practicesoftwaretesting.com"
$env:API_URL="https://api-with-bugs.practicesoftwaretesting.com"
$env:ROUTE_PREFIX="/#"
pytest --tracing retain-on-failure --screenshot only-on-failure
```

Không sửa test giữa hai lần chạy. Khác biệt môi trường được xử lý bằng biến môi trường và fixture, không bao giờ nằm trong test.

### 4.2 Đỏ trên BUGGY chưa chắc là lỗi

| Khác biệt | PROD | BUGGY | Repo xử lý thế nào |
|---|---|---|---|
| Đường dẫn trang | `/auth/login` | `/#/auth/login` | `ROUTE_PREFIX=/#`, ghép trong `BasePage.open()` |
| Dữ liệu đăng ký | `address` là object | `address`, `city`, `country`, `postcode` để phẳng | `register_user()` thử cả hai kiểu |
| Bộ dữ liệu | 50 sản phẩm, id chuỗi | 26 sản phẩm, id số | Assertion không dùng con số tuyệt đối |
| API giỏ hàng | có `/carts` | không có | Ghi nhận là khác môi trường |
| Nơi lưu token | localStorage | sessionStorage | Ghi nhận là khác môi trường |

Một điều thú vị: test viết "thô" gọi thẳng `page.goto("/auth/login")` sẽ đỏ trên BUGGY, còn bản dùng page object thì không. Đó là lợi ích của việc mọi điều hướng đi qua một chỗ.

### 4.3 Phân loại mỗi test đỏ

| Loại | Điều kiện | Tính điểm đồ án? |
|---|---|---|
| Lỗi thật | Xanh trên PROD, đỏ trên BUGGY, hành vi sai so với nghiệp vụ, có bằng chứng | Có |
| Khác dữ liệu | Số lượng, id, tên sản phẩm khác | Không. Sửa assertion cho bớt phụ thuộc dữ liệu |
| Khác môi trường | Đường dẫn, API thiếu, nơi lưu token | Không |
| Test sai, site chậm | Timeout, 502, assertion viết sai | Không. Sửa test hoặc chạy lại có trace |

Nhiều test đỏ vì cùng một lỗi thì chỉ tính một lỗi.

### 4.4 Bộ test xanh trên BUGGY là đang bỏ sót

BUGGY cố ý có lỗi. Nếu bộ test của em xanh hết trên BUGGY, nghĩa là assertion còn lỏng hoặc chưa chạm tới chức năng có lỗi. Cách sửa là **siết assertion**, không phải viết thêm test cho đủ số.

Ví dụ trên lớp: sau khi thêm sản phẩm vào giỏ, Toolshop hiện một thông báo.

```python
# Lỏng: thông báo nào hiện ra cũng xanh, kể cả thông báo lỗi
expect(product.toast.first).to_be_visible()

# Chặt: chỉ xanh khi đúng nội dung thông báo thành công
expect(product.toast.first).to_have_text("Product added to shopping cart.")
```

Câu hỏi để siết từng assertion:

- Test này chứng minh đúng điều gì? Nếu hệ thống trả sai giá trị, test có đỏ không?
- Kiểm "có hiện ra" hay kiểm "hiện đúng nội dung"?
- Kiểm tổng hay kiểm từng dòng?
- Có cách nào kiểm mà không dựa vào con số cố định? Ví dụ hỏi API `total` và `per_page` rồi suy ra giao diện phải có gì.

### 4.5 Báo cáo lỗi

Mỗi lỗi trong `docs/BUG_REPORT.md` có đủ:

| Trường | Viết gì |
|---|---|
| Mã lỗi | `BUG-001` |
| Chức năng | Tìm kiếm, giỏ hàng, đăng nhập, ... |
| Các bước tái hiện | Đánh số, ai đọc cũng làm lại được bằng tay |
| Kết quả mong đợi | Theo nghiệp vụ, đối chiếu PROD |
| Kết quả thực tế | Trên BUGGY, ghi đúng chữ, đúng số |
| Test phát hiện | `tests/...::test_...` |
| Bằng chứng | Ảnh chụp hoặc trace, đặt trong `docs/screenshots/` |

Tiêu chuẩn của một báo cáo tốt: người khác làm theo các bước của em và tái hiện được. Ở công ty, báo cáo lỗi không tái hiện được sẽ bị trả lại.

## 5. AI trong kiểm thử tự động

### 5.1 Playwright MCP

MCP (Model Context Protocol) cho phép trợ lý AI điều khiển một trình duyệt thật: mở trang, đọc cấu trúc trang, bấm, gõ. Nhờ vậy AI đề xuất locator dựa trên trang thật thay vì đoán.

VS Code với GitHub Copilot, tạo `.vscode/mcp.json`:

```json
{ "servers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } } }
```

Claude Code: `claude mcp add playwright npx @playwright/mcp@latest`.

Không có các công cụ trên thì dùng chatbot bất kỳ: dán đoạn HTML của form (F12, Copy outerHTML) cùng yêu cầu.

### 5.2 Soát code AI viết

| Kiểm | AI hay làm sai |
|---|---|
| Locator | Dùng class CSS, XPath, `text=` thay vì data-test hoặc role |
| Chờ | Chèn `sleep` hoặc `wait_for_timeout` |
| Assertion | Chỉ kiểm "hiện ra", không kiểm nội dung |
| Bịa | Data-test hoặc endpoint không tồn tại |
| Cấu trúc | Bỏ qua page object, viết locator thẳng trong test |
| Kiến thức nghiệp vụ | Không biết các quy tắc riêng, ví dụ ô đính kèm của form liên hệ Toolshop chỉ nhận tệp rỗng |

### 5.3 Giới hạn và rủi ro

- AI không biết nghiệp vụ và dữ liệu test của nhóm. Nó viết test "xanh" mà không chứng minh gì.
- Không dán mật khẩu, token, khoá thật vào AI. Không commit `.vscode/mcp.json` nếu có thông tin riêng.
- Code AI viết mà em đứng tên, em vẫn phải giải thích được từng dòng khi vấn đáp.

Cách làm cho đồ án: commit bản AI sinh ra nguyên vẹn, soát, sửa, commit lần hai. Trong README ghi bảng: AI viết gì, sai ở đâu, em sửa thế nào và vì sao.

## 6. Tự kiểm tra

1. `inner_text()` và `expect(...).to_have_text()` khác nhau ở đâu?
2. Kể 3 điều Playwright chờ trước khi bấm một nút.
3. Chạy song song làm tăng test chập chờn qua những cơ chế nào?
4. Chạy lại test bị đỏ có chữa được flaky không? Nó có thể che giấu điều gì?
5. Một test đỏ trên BUGGY vì trang đăng nhập trắng. Đó là lỗi thật hay khác môi trường? Em kiểm chứng thế nào?
6. Chọn một test của nhóm em đang xanh trên BUGGY. Assertion nào có thể siết chặt hơn?
7. CI xanh nhưng người dùng vẫn báo lỗi. Em rà soát từ đâu?

## 7. Liên hệ đồ án

- Mục 3.11 Flaky test, 3.12 Regression trên BUGGY (1,5 điểm, cao nhất), 3.13 Cách tính lỗi, mục 6 Sử dụng AI.
- Câu vấn đáp 11, 13, 14, 15, 16.

## 8. Đọc thêm

- Gỡ lỗi: https://playwright.dev/python/docs/debug
- Trace Viewer: https://playwright.dev/python/docs/trace-viewer
- Auto-waiting: https://playwright.dev/python/docs/actionability
- Playwright MCP: https://github.com/microsoft/playwright-mcp
- pytest-rerunfailures: https://pypi.org/project/pytest-rerunfailures/
