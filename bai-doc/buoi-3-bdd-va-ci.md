# Bài đọc buổi 3 - BDD với pytest-bdd, CI với GitHub Actions

Đọc sau buổi học ngày 18/11. Thời gian đọc khoảng 30 phút. Code đã chạy thật trên Toolshop; workflow lấy từ bộ bài giải.

Sau bài này, em làm được:

1. Viết file `.feature` bằng Gherkin, có `Scenario Outline` và `Examples`.
2. Viết step definition bằng pytest-bdd, gọi lại page object.
3. Nói được BDD mang lại gì và tốn gì.
4. Viết workflow GitHub Actions chạy 3 trình duyệt, giữ lại báo cáo, và chặn Pull Request khi đỏ.

## 1. Vì sao có BDD

Câu yêu cầu "Đơn hàng trên 100 đô được giảm giá" có thể được hiểu ba kiểu:

- Product Owner: từ 100 đô trở lên, giảm 10% trên tổng trước thuế.
- Lập trình viên: lớn hơn 100, giảm 10 đô, tính sau thuế.
- Tester: đúng 100 thì sao? Có mã giảm giá khác thì cộng dồn không?

BDD (Behavior-Driven Development) là thói quen viết kịch bản bằng ngôn ngữ chung **trước** khi code, để ba vai trên hiểu giống nhau. Buổi họp ba vai cùng viết kịch bản gọi là Three Amigos.

## 2. Gherkin

```gherkin
Feature: Product search
  As a shopper
  I want to search products by name
  So that I find the tool I need quickly

  Background:
    Given I am on the home page

  Scenario Outline: Search returns only matching products
    When I search for "<keyword>"
    Then the search caption mentions "<keyword>"
    And every product name contains "<keyword>"

    Examples:
      | keyword |
      | pliers  |
      | hammer  |
      | saw     |

  Scenario: Search with an unknown word shows the empty state
    When I search for "zzz-no-such-tool"
    Then I see the message "There are no products found."
```

| Từ khoá | Ý nghĩa |
|---|---|
| `Feature` | Chức năng, kèm câu chuyện người dùng 3 dòng: As a, I want, So that |
| `Background` | Các bước chạy trước mọi kịch bản trong file |
| `Scenario` | Một kịch bản cụ thể |
| `Scenario Outline` + `Examples` | Một kịch bản chạy nhiều lần, mỗi dòng bảng một lần. `<keyword>` được thay bằng giá trị trong bảng |
| `Given` | Trạng thái ban đầu |
| `When` | Hành động của người dùng |
| `Then` | Kết quả quan sát được |
| `And` | Thêm một bước cùng loại với bước trước |

### Viết Gherkin tốt

1. Câu nói về nghiệp vụ, không nói về giao diện. Sai: `When I click the button with data-test search-submit`. Đúng: `When I search for "saw"`.
2. Mỗi kịch bản một hành vi, khoảng 3 đến 7 bước.
3. `Then` mô tả thứ người dùng thấy được, đủ cụ thể để kiểm.

## 3. pytest-bdd

### 3.1 Từ câu Gherkin tới page object

```
search.feature           When I search for "saw"
       |
step definition          @when(parsers.parse('I search for "{keyword}"'))
       |
page object              home.search(keyword)
```

Step chỉ gọi page object và kiểm kết quả. Nếu thấy mình cần viết `page.get_by_test_id(...)` trong step, locator đó đang thiếu trong `pages/`.

### 3.2 Step definition

```python
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

# Đường dẫn tính từ bdd_features_base_dir trong pytest.ini (tests/buoi3/features)
scenarios("search.feature")


@given("I am on the home page", target_fixture="home")
def home(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('I search for "{keyword}"'))
def search(home, keyword):
    home.search(keyword)


@then(parsers.parse('every product name contains "{keyword}"'))
def names_contain(home, keyword):
    expect(home.search_completed).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names and all(keyword.lower() in n.lower() for n in names), names
```

| Thành phần | Tác dụng |
|---|---|
| `scenarios("search.feature")` | Sinh một test pytest cho mỗi kịch bản, mỗi dòng Examples |
| `@given`, `@when`, `@then` | Gắn hàm với một câu Gherkin |
| `parsers.parse('... "{keyword}"')` | Lấy giá trị trong câu ra thành tham số |
| `{quantity:d}` | Lấy ra số nguyên. Thiếu `:d` thì nhận được chuỗi `"3"` |
| `target_fixture="home"` | Giá trị hàm trả về thành fixture tên `home` cho các bước sau |

`target_fixture` là cách chuyền dữ liệu giữa các bước. Ví dụ đọc đơn giá trước khi thêm vào giỏ, để bước `Then` so sánh:

```python
@when(parsers.parse("I add it to the cart with quantity {quantity:d}"), target_fixture="unit_price")
def add_to_cart(product_page, quantity):
    unit = product_page.price()
    product_page.add_to_cart(quantity=quantity)
    return unit
```

### 3.3 Đọc lỗi thiếu step

```
E   pytest_bdd.exceptions.StepDefinitionNotFoundError: Step definition is not found:
    Then "the search caption mentions "pliers"". Line 11 in scenario "Search returns only matching products"
```

pytest-bdd chỉ đúng câu nào chưa có code. Cách làm hiệu quả: viết feature trước, chạy, rồi viết từng step theo danh sách lỗi.

### 3.4 Được gì, mất gì

| Được | Mất |
|---|---|
| Product Owner đọc hiểu được kịch bản | Thêm một tầng gián tiếp giữa yêu cầu và code |
| Tài liệu luôn đúng, vì nó chạy được | Kho step phình to, khó tìm, dễ trùng |
| Một kịch bản, nhiều dòng dữ liệu | Dễ biến thành "Gherkin hoá từng cú click", vô nghĩa với người đọc |

Đồ án yêu cầu một luồng nghiệp vụ viết BDD. Phần còn lại viết pytest thường.

## 4. CI với GitHub Actions

### 4.1 Khái niệm

| Thuật ngữ | Nghĩa |
|---|---|
| Workflow | Một file YAML trong `.github/workflows/`, mô tả việc tự động |
| Trigger | Sự kiện kích hoạt: push, pull request, bấm tay |
| Job | Một nhóm bước chạy trên một máy |
| Step | Một lệnh hoặc một action có sẵn |
| Runner | Máy ảo của GitHub chạy job, ví dụ `ubuntu-latest` |
| Matrix | Chạy cùng một job với nhiều cấu hình, ví dụ 3 trình duyệt |
| Artifact | File giữ lại sau khi chạy: báo cáo, trace, ảnh chụp |

### 4.2 Workflow của đồ án

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

env:
  BASE_URL: http://localhost:4200      # Toolshop tự dựng trong job, xem mục 4.3
  API_URL: http://localhost:8091
  GITHUB_API_URL: https://api.github.com
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  test:
    name: test (${{ matrix.browser }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v4
      - run: docker compose -f toolshop/docker-compose.yml up -d
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt
      - run: playwright install --with-deps ${{ matrix.browser }}
      - run: bash toolshop/start.sh
      - run: >
          pytest --browser ${{ matrix.browser }}
          -n 2 --reruns 1 --reruns-delay 2
          --tracing retain-on-failure --screenshot only-on-failure
          --html=report.html --self-contained-html
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: report-${{ matrix.browser }}
          path: |
            report.html
            test-results/
          retention-days: 7
```

Mỗi dòng quan trọng và lý do:

| Dòng | Vì sao |
|---|---|
| 3 trigger trong `on:` | Chạy khi vào `main`, trên mọi Pull Request, và bấm tay khi cần chạy lại |
| `env: BASE_URL, API_URL` | URL nằm ở cấu hình, không nằm trong code (đề trừ 1 điểm nếu viết cứng). Nhờ vậy cùng bộ test chạy được trên site công khai ở máy em và trên Toolshop tự dựng ở CI |
| `docker compose ... up -d` | Khởi động Toolshop riêng của job ngay từ đầu, để giao diện biên dịch trong lúc job cài Python và trình duyệt |
| `bash toolshop/start.sh` | Nạp dữ liệu mẫu mới và chờ tới khi UI, API trả lời. Chạy test trước lúc này thì đỏ hàng loạt |
| `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` | GitHub tự cấp token cho mỗi lượt chạy. Máy chạy CI dùng chung IP với nhiều người, không có token thì test GitHub API bị chặn vì hết lượt |
| `fail-fast: false` | Firefox đỏ không huỷ WebKit đang chạy, giữ đủ thông tin để chẩn đoán |
| `--with-deps` | Cài thư viện hệ thống. Thiếu thì WebKit không chạy |
| `-n 2` | Chạy 2 test song song, vừa sức máy chạy của GitHub và Toolshop trong job |
| `--reruns 1` | Chịu được một lần lỗi mạng. Không đặt cao hơn để che test sai |
| `--tracing retain-on-failure`, `--screenshot only-on-failure` | Chỉ giữ bằng chứng của test đỏ, artifact gọn |
| `if: always()` | Bước sau mặc định bị bỏ khi bước trước đỏ, mà test đỏ là lúc cần báo cáo nhất |
| `name: report-${{ matrix.browser }}` | Ba job cùng tên `report` thì bước upload báo lỗi |
| `retention-days: 7` | Không giữ artifact quá lâu |

### 4.3 Vì sao CI tự dựng Toolshop

Site công khai practicesoftwaretesting.com đứng sau Cloudflare. Cloudflare coi trình duyệt không giao diện chạy từ máy chủ của GitHub là bot và trả về trang "Performing security verification" thay cho Toolshop. Khi thử chạy trên site công khai, 41/59 test Chromium đỏ vì trang này, Firefox và WebKit cũng thỉnh thoảng dính. Ở máy em thì không sao.

Doanh nghiệp xử lý đúng như vậy: CI không test vào hệ thống dùng chung mà tự dựng một môi trường test riêng cho mỗi lượt chạy. Được ba điều:

1. Không bị chặn, không phụ thuộc site công khai có sống hay không.
2. Dữ liệu sạch mỗi lần: tài khoản mẫu không bị ai khoá, giỏ hàng không bị ai thêm đồ.
3. Kết quả lặp lại được: đỏ là do code, không phải do mạng.

Thư mục `toolshop/` trong repo lo việc này bằng Docker image chính chủ của Testsmith: `sprint5` là PROD, `sprint5-with-bugs` là BUGGY. Em không cần sửa gì trong đó. Nếu máy em có Docker, có thể dựng y như CI:

```bash
bash toolshop/start.sh                                   # PROD
SPRINT=sprint5-with-bugs bash toolshop/start.sh          # hoặc BUGGY
BASE_URL=http://localhost:4200 API_URL=http://localhost:8091 pytest
docker compose -f toolshop/docker-compose.yml down       # tắt và xoá
```

Testsmith chỉ cho dùng mã nguồn này nội bộ, phi thương mại. Không mở Toolshop tự dựng ra Internet.

### 4.4 Chặn Pull Request khi đỏ

Settings, Branches, thêm quy tắc cho `main`:

1. Require a pull request before merging, kèm ít nhất 1 người duyệt.
2. Require status checks to pass: chọn `test (chromium)`, `test (firefox)`, `test (webkit)`.

Từ đó, không ai đẩy thẳng lên `main` được, và nút Merge bị khoá khi còn check đỏ. Luồng làm việc:

```bash
git switch -c feature/<tên>-<việc>
# sửa code, chạy pytest ở máy
git add . && git commit -m "Add CartPage and line price test"
git push -u origin feature/<tên>-<việc>
# mở Pull Request trên GitHub, nhờ bạn review, chờ CI xanh, merge
```

### 4.5 Đọc kết quả

1. Tab Actions, mở lượt chạy, xem job nào đỏ.
2. Kéo xuống phần Artifacts, tải `report-<trình duyệt>`.
3. Mở `report.html` bằng trình duyệt để xem test nào đỏ và thông báo lỗi.
4. Giải nén `test-results/`, mở trace: `playwright show-trace test-results/<tên-test>/trace.zip`.
5. Trace Viewer cho xem từng bước: ảnh DOM trước và sau, request mạng, console.

Badge CI cho README:

```markdown
![CI](https://github.com/<tài-khoản>/<repo>/actions/workflows/ci.yml/badge.svg)
```

### 4.6 Không commit rác

`.gitignore` tối thiểu:

```
__pycache__/
.venv/
.pytest_cache/
test-results/
report*.html
.env
```

Kiểm tra: `git ls-files | grep -E "test-results|\.venv|__pycache__|report.*html"` phải rỗng. Đề trừ 0,5 điểm nếu commit các thư mục này.

## 5. Lỗi thường gặp

| Triệu chứng | Nguyên nhân |
|---|---|
| Thêm file feature mà không có test mới | Chưa thêm tên file vào `scenarios(...)` |
| `fixture 'product_page' not found` | Bước trước quên `target_fixture` |
| So sánh số lượng luôn sai | Thiếu `:d`, nhận chuỗi thay vì số |
| File step không chạy, vẫn "xanh" | Tên file không bắt đầu bằng `test_` nên pytest bỏ qua |
| Workflow không chạy | YAML sai thụt lề, hoặc thiếu `on:` |
| WebKit đỏ hết từ đầu | Thiếu `--with-deps` |
| `git push` bị từ chối | Đúng như mong muốn khi đã bảo vệ `main`: đi qua nhánh và Pull Request |

## 6. Tự kiểm tra

1. `Scenario Outline` khác `Scenario` ở đâu?
2. `target_fixture` dùng để làm gì? Cho một ví dụ trên Toolshop.
3. Vì sao step definition không nên chứa locator mới?
4. Vì sao đồ án cần `fail-fast: false` và tên artifact riêng cho từng trình duyệt?
5. Bỏ `if: always()` ở bước upload thì chuyện gì xảy ra khi có test đỏ?
6. Một test chỉ đỏ trên WebKit. Em sẽ mở những gì, theo thứ tự nào?

## 7. Liên hệ đồ án

- Mục 3.7 BDD, 3.8 Git và GitHub, 3.9 GitHub Actions, 3.10 Báo cáo và artifact.
- Câu vấn đáp 9, 12, 13.

## 8. Đọc thêm

- pytest-bdd: https://pytest-bdd.readthedocs.io/
- Gherkin: https://cucumber.io/docs/gherkin/reference/
- GitHub Actions: https://docs.github.com/en/actions
- Playwright trên CI: https://playwright.dev/python/docs/ci
- Trace Viewer: https://playwright.dev/python/docs/trace-viewer
