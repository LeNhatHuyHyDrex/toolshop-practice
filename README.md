# Toolshop Practice - bài thực hành 4 buổi (Automation Testing)

Repo này là "phòng lab" trên lớp. Mỗi buổi có một thư mục bài tập trong `tests/`. Bài nào chưa làm sẽ đỏ (`NotImplementedError`), làm xong thì xanh. Mục tiêu mỗi buổi: biến đỏ thành xanh, đúng luật.

Hệ thống kiểm thử: Toolshop https://practicesoftwaretesting.com (PROD) và https://with-bugs.practicesoftwaretesting.com (BUGGY).

## 1. Cài đặt (làm ở nhà trước buổi 1, khoảng 15 phút)

Cần Python 3.12, Git và một tài khoản GitHub.

**Tạo repo của em từ repo lớp:** mở https://github.com/jameboykks/toolshop-practice, bấm **Use this template**, chọn **Create a new repository**, đặt tên `toolshop-practice`, chọn **Public**. Repo của em có sẵn toàn bộ bài tập và là nơi em đẩy code, chạy CI ở buổi 3. Sau đó clone repo của em về máy:

Windows (PowerShell):

```powershell
git clone https://github.com/<tài-khoản-của-em>/toolshop-practice.git
cd toolshop-practice
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
python tools/doctor.py
```

macOS / Linux:

```bash
git clone https://github.com/<tài-khoản-của-em>/toolshop-practice.git
cd toolshop-practice
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
python tools/doctor.py
```

`tools/doctor.py` kiểm Python, thư viện, trình duyệt, tệp `.env`, kết nối tới Toolshop và GitHub, Git và Node.js. Thấy dòng "Máy đã sẵn sàng" là xong. Dòng nào ghi `[LỖI]` thì làm theo gợi ý ngay bên dưới rồi chạy lại.

Chạy thử bộ test mẫu: `pytest tests/buoi1/test_b1_spaghetti.py` phải ra `4 passed`.

Cần cài thêm trước buổi 4: Node.js bản LTS (https://nodejs.org/), dùng cho Playwright MCP.

Nên làm trước buổi 2: tạo token GitHub (github.com, Settings, Developer settings, Fine-grained tokens, Generate, không cần chọn quyền nào) rồi điền vào dòng `GITHUB_TOKEN=` trong `.env`. Không có token, cả lớp dùng chung mạng trường chỉ được gọi GitHub API 60 lần mỗi giờ.

URL của hệ thống nằm trong tệp `.env` (BASE_URL, API_URL, ROUTE_PREFIX), không bao giờ nằm trong code. Biến đặt trong terminal sẽ được ưu tiên hơn `.env`. Tệp `.env` không được commit.

## 2. Lệnh hay dùng

```bash
pytest tests/buoi1                         # chạy cả buổi 1
pytest tests/buoi1 -k b1_3                 # chỉ bài B1.3
pytest tests/buoi1 -k b1_3 --headed --slowmo 300   # xem trình duyệt chạy chậm
pytest -m smoke                            # chỉ test gắn nhãn smoke
pytest -n auto                             # chạy song song
pytest --tracing on -k b1_4                # ghi trace
playwright show-trace test-results/<tên-test>/trace.zip
playwright codegen https://practicesoftwaretesting.com   # tìm locator
```

## 3. Cấu trúc

```
pages/          page object (BasePage có sẵn, các trang khác có TODO)
tests/buoi1/    Page Object Model
tests/buoi2/    API Toolshop, API GitHub, route / mock, API + UI
tests/buoi3/    BDD (pytest-bdd) - features/ + step definitions
tests/buoi4/    assertion lỏng cần siết để bắt lỗi trên BUGGY
clinic/         "phòng khám flaky" - 5 test bệnh cần chẩn đoán
data/           dữ liệu JSON cho test data-driven
bai-doc/        bài đọc ôn tập mỗi buổi (đọc sau buổi học)
docs/           mẫu BUG_REPORT.md
.github/        workflows/ci.yml.todo có chỗ trống (buổi 3, điền xong đổi tên thành ci.yml), mẫu Pull Request
tools/doctor.py kiểm tra máy trước buổi học
toolshop/       Toolshop chạy bằng Docker cho CI (buổi 3): không cần sửa, xem bai-doc buổi 3 mục 4.3
conftest.py     fixture dùng chung: api, github, test_user, auth_token, auth_headers, logged_in_page
```

## 4. Luật chơi (giống đồ án cuối kỳ)

1. Locator chỉ nằm trong `pages/`. Assertion chỉ nằm trong `tests/`.
2. Không `time.sleep()`, không `wait_for_timeout()`. Chờ bằng `expect()` hoặc `expect_response()`.
3. Không assert số lượng tuyệt đối hay id cụ thể: PROD có 50 sản phẩm, BUGGY có 26.
4. Mỗi test có docstring 3 ý: mục tiêu, tiền điều kiện, kết quả mong đợi.
5. Không dùng tài khoản dùng chung (`customer@`, `customer2@`, `admin@`) trong test. Test cần đăng nhập dùng tài khoản riêng do fixture `test_user` tạo. Test đăng nhập sai dùng email không tồn tại: Toolshop đếm số lần đăng nhập sai và có thể khoá tài khoản, nếu thử sai trên tài khoản dùng chung là khoá luôn cho cả lớp.

## 5. Chạy trên BUGGY (buổi 4)

BUGGY dùng hash routing (`/#/auth/login`), nên cần thêm `ROUTE_PREFIX`:

```bash
# macOS / Linux
BASE_URL=https://with-bugs.practicesoftwaretesting.com API_URL=https://api-with-bugs.practicesoftwaretesting.com ROUTE_PREFIX=/# pytest tests/buoi4
```

```powershell
# Windows PowerShell
$env:BASE_URL="https://with-bugs.practicesoftwaretesting.com"; $env:API_URL="https://api-with-bugs.practicesoftwaretesting.com"; $env:ROUTE_PREFIX="/#"; pytest tests/buoi4
```

Mở terminal mới (hoặc xoá 3 biến) để quay lại PROD.

Trên CI không dùng site công khai: Cloudflare chặn trình duyệt chạy trên máy của GitHub. Mỗi job tự dựng Toolshop bằng Docker (thư mục `toolshop/`). Job BUGGY chỉ cần `SPRINT: sprint5-with-bugs` và `ROUTE_PREFIX: /#` trong `env:`.

## 6. Nhận bài giải sau mỗi buổi

Sau mỗi buổi, thầy đưa bài giải vào repo lớp. Repo của em tạo từ template nên không tự cập nhật; lấy đúng các tệp cần bằng git (chỉ những tệp được nêu bị thay, bản em tự làm vẫn còn trong lịch sử commit):

```bash
git remote add lop https://github.com/jameboykks/toolshop-practice.git   # làm một lần
git fetch lop
git checkout lop/main -- pages tests/buoi1/test_b1_pom.py               # ví dụ: sau buổi 1
git commit -m "Take the session 1 reference solution"
```

| Sau buổi | Đường dẫn cần lấy |
|---|---|
| 1 | `pages tests/buoi1/test_b1_pom.py` |
| 2 | `tests/buoi2` |
| 3 | `tests/buoi3 .github/workflows/ci.yml` |
| 4 | `clinic/test_clinic_fixed.py` |

Muốn so bài của em với bài giải trước khi lấy: `git diff HEAD lop/main -- pages`.

## 7. Bài đọc

Thư mục `bai-doc/` có một bài đọc cho mỗi buổi (25 - 35 phút), cuối bài có câu hỏi tự kiểm tra. Đọc sau buổi học để ôn và trước khi làm phần đồ án tương ứng.

## 8. Bị kẹt?

- Đọc dòng `E ` trong output trước: nó nói locator nào, chờ gì, nhận được gì.
- Chạy `--headed --slowmo 500` để xem.
- Mở trace.
- Sau mỗi buổi giảng viên phát bản `pages/` hoàn chỉnh để ai chậm vẫn theo kịp buổi sau.
