# Bài đọc buổi 1 - Page Object Model

Đọc sau buổi học ngày 04/11 để ôn lại, và trước khi làm Sprint 1 của đồ án. Thời gian đọc khoảng 25 phút. Mọi đoạn code dưới đây đã chạy thật trên Toolshop.

Sau bài này, em làm được:

1. Giải thích Page Object Model (POM) giải quyết vấn đề gì và phải đánh đổi gì.
2. Viết `BasePage` và các page object cho Toolshop đúng ba quy tắc.
3. Chọn locator theo thứ tự ưu tiên và xử lý lỗi strict mode.
4. Tránh các bẫy riêng của Toolshop.

## 1. Vấn đề: locator nằm rải trong test

Đây là một test viết "thô", lấy từ `tests/buoi1/test_b1_spaghetti.py`:

```python
def test_spaghetti_add_two_hammers(page):
    page.goto("/")
    expect(page.get_by_test_id("product-name").first).to_be_visible()
    page.get_by_test_id("product-name").filter(has_text=re.compile(r"^\s*Claw Hammer\s*$")).click()
    expect(page.get_by_test_id("product-name")).to_have_text("Claw Hammer")
    page.get_by_test_id("quantity").fill("2")
    page.get_by_test_id("add-to-cart").click()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("2")
```

Test này chạy đúng. Vấn đề nằm ở chỗ nó trộn hai loại thông tin:

- **Phần tử ở đâu, thao tác thế nào:** `get_by_test_id("product-name")`, `fill("2")`.
- **Kết quả đúng là gì:** badge giỏ hàng phải là `2`.

Viết 50 test như vậy thì `product-name` lặp lại hàng chục lần. Ngày Toolshop đổi tên thuộc tính đó, em phải sửa hàng chục chỗ, và chỉ cần sót một chỗ là test đỏ dù ứng dụng không có lỗi. Trong file mẫu, `product-name` xuất hiện ở 9 dòng.

## 2. Page Object Model là gì

Mỗi trang (hoặc mỗi thành phần dùng lại được như header) là một class. Class đó biết hai thứ: phần tử nằm ở đâu (locator), và người dùng làm gì trên trang (action). Test chỉ còn kịch bản và kỳ vọng.

```
tests/        kết quả đúng là gì           expect(...), assert
   |
pages/        phần tử ở đâu, làm thế nào   get_by_test_id(...), click(), fill()
   |
Playwright    tự chờ, điều khiển trình duyệt
   |
Trình duyệt   Toolshop
```

Cùng test ở trên, viết theo POM:

```python
def test_product_add_quantity_two_updates_cart_badge(page):
    """Goal: add-to-cart uses the chosen quantity.
    Precondition: none.
    Expected: the cart badge shows 2."""
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_have_text("Claw Hammer")
    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")
```

Toolshop đổi tên `product-name`: em sửa 2 dòng trong `pages/` (một ở HomePage, một ở ProductPage), không đụng test nào.

**Cái giá phải trả:** thêm một tầng code, phải đặt tên cho mọi thứ, và với một test viết một lần rồi bỏ thì POM tốn công hơn được. Với bộ test sống lâu như đồ án, POM gần như luôn đáng.

## 3. Ba quy tắc của page object

### 3.1 Locator khai báo một lần, trong `__init__`

```python
class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name = page.get_by_test_id("product-name")
        self.unit_price = page.get_by_test_id("unit-price")
        self.quantity = page.get_by_test_id("quantity")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")
```

Locator của Playwright là "lười": khai báo chưa tìm phần tử nào cả. Chỉ khi em gọi `click()`, `fill()` hay `expect(...)` thì Playwright mới tìm, và tìm lại mỗi lần. Vì vậy khai báo hết trong `__init__` không tốn gì và không bị "cũ".

### 3.2 Action trả về một page object

```python
def add_to_cart(self, quantity: int = 1):
    if quantity != 1:
        self.quantity.fill(str(quantity))
    self.add_to_cart_button.click()
    return self
```

Ở lại trang cũ thì trả về `self`. Chuyển trang thì trả về page object của trang mới. Nhờ vậy test viết được thành chuỗi và đọc như kịch bản:

```python
cart = (HomePage(page).open()
        .open_product("Hammer")
        .add_to_cart()
        .go_to_cart())
```

Quên `return self` là lỗi hay gặp nhất: dòng sau báo `'NoneType' object has no attribute ...`.

### 3.3 Không assert trong page object

Có ba lý do:

1. Một hành động phục vụ nhiều kỳ vọng khác nhau. `add_to_cart()` dùng cho test "thêm thành công", "thêm khi hết hàng", "thêm khi chưa đăng nhập". Kỳ vọng mỗi test khác nhau nên không thể nằm trong hành động.
2. Giao diện đổi và kỳ vọng nghiệp vụ đổi là hai lý do khác nhau. Mỗi file chỉ nên có một lý do để sửa.
3. Khi đỏ, lỗi chỉ thẳng vào test. Người đọc biết ngay test nào mong điều gì.

**Chờ thì được.** `HomePage.open()` trong repo chờ danh sách sản phẩm đầu tiên tải xong rồi mới trả về. Đó là đồng bộ (đợi trang sẵn sàng), không phải kiểm chứng (khẳng định đúng sai). Lý do cần chờ: xem mục 6.

Tự kiểm tra quy tắc bất cứ lúc nào:

```bash
grep -rn "expect(\|assert " pages/          # phải rỗng
grep -rn "get_by_\|locator(" tests/          # chỉ được có trong test "thô" mẫu
grep -rn "sleep\|wait_for_timeout" tests pages   # phải rỗng
```

## 4. BasePage: phần chung của mọi trang

```python
class BasePage:
    path = "/"
    # PROD dùng /auth/login, BUGGY dùng /#/auth/login. conftest.py đặt giá trị này từ ROUTE_PREFIX.
    route_prefix = ""

    def __init__(self, page: Page):
        self.page = page
        self.nav_cart = page.get_by_test_id("nav-cart")
        self.cart_quantity = page.get_by_test_id("cart-quantity")
        self.nav_sign_in = page.get_by_test_id("nav-sign-in")
        self.toast = page.get_by_role("alert")

    def open(self):
        self.page.goto(self.route_prefix + self.path)
        return self

    def go_to_cart(self):
        from pages.cart_page import CartPage

        self.nav_cart.click()
        return CartPage(self.page)
```

Những điểm cần hiểu:

- `page` được truyền vào. Page object không tự mở trình duyệt, không biết browser hay context.
- Mỗi trang con chỉ khai báo `path` của nó (`/checkout`, `/auth/login`). `open()` dùng chung.
- `route_prefix` là lý do em sẽ chạy được cùng bộ test trên môi trường BUGGY ở buổi 4, chỉ bằng một biến môi trường. Mọi điều hướng đi qua `open()` nên chỉ cần sửa một chỗ.
- `import` đặt bên trong hàm để hai file không import vòng lẫn nhau.
- Toast thông báo của Toolshop không có data-test, nên dùng vai trò ARIA: `get_by_role("alert")`.

## 5. Chọn locator

### 5.1 Thứ tự ưu tiên

| Ưu tiên | Locator | Khi nào dùng |
|---|---|---|
| 1 | `get_by_test_id("add-to-cart")` | Dev đã gắn `data-test`. Bền nhất, vì nó là "hợp đồng" giữa dev và tester |
| 2 | `get_by_role("button", name="Add to cart")` | Phần tử có vai trò rõ ràng. Giống cách người dùng nhìn trang |
| 3 | `get_by_label("Email address")`, `get_by_placeholder(...)` | Ô nhập trong form |
| 4 | CSS: `locator("a.card")` | Không còn cách nào ở trên |
| 5 | XPath | Gần như không bao giờ |

Vì sao `data-test` tốt hơn class CSS: class CSS phục vụ giao diện và đổi theo thiết kế; `data-test` chỉ tồn tại để test dùng, chỉ đổi khi có chủ đích.

Toolshop dùng thuộc tính `data-test` (không phải `data-testid` mặc định của Playwright). Repo đã cấu hình một lần trong `conftest.py`:

```python
@pytest.fixture(scope="session", autouse=True)
def configure_playwright(playwright):
    playwright.selectors.set_test_id_attribute("data-test")
```

Tìm locator nhanh: `playwright codegen https://practicesoftwaretesting.com`, bấm vào phần tử, Playwright đề xuất locator.

### 5.2 Các data-test chính của Toolshop

| Trang | data-test |
|---|---|
| Trang chủ | `search-query`, `search-submit`, `search-caption`, `search-result-count`, `search_completed`, `no-results`, `sort`, `sorting_completed`, `product-name`, `product-price`, `pagination-next` |
| Chi tiết sản phẩm | `product-name` (thẻ h1), `unit-price`, `quantity`, `increase-quantity`, `add-to-cart` |
| Giỏ hàng `/checkout` | `product-title`, `product-quantity`, `line-price`, `cart-total`, `continue-shopping`, `proceed-1` |
| Đăng nhập | `email`, `password`, `login-submit`, `login-error`, `email-error`, `password-error` |
| Liên hệ | `first-name`, `last-name`, `email`, `subject`, `message`, `attachment`, `contact-submit` |
| Header | `nav-home`, `nav-contact`, `nav-sign-in`, `nav-cart`, `cart-quantity`, `nav-menu` |

`search_completed`, `sorting_completed`, `filter_completed` là các phần tử Toolshop hiện ra khi tìm kiếm, sắp xếp, lọc xong. Chúng sinh ra để tester đồng bộ: đọc kết quả sau khi thấy chúng.

### 5.3 Strict mode

```
Error: strict mode violation: get_by_test_id("product-name") resolved to 9 elements
```

Playwright từ chối thao tác khi locator khớp nhiều hơn một phần tử, để em không bấm nhầm. Chọn rõ phần tử nào:

| Cách | Ví dụ |
|---|---|
| Phần tử đầu tiên | `product_names.first` |
| Theo vị trí | `product_names.nth(2)` |
| Theo nội dung | `product_names.filter(has_text="Hammer")` |

## 6. Bẫy riêng của Toolshop

| Bẫy | Biểu hiện | Cách tránh |
|---|---|---|
| Chữ ECO nằm trong tiêu đề | Sản phẩm thân thiện môi trường hiện "Wood Saw ECO" trong cùng thẻ h1, `to_have_text("Wood Saw")` đỏ | `to_contain_text("Wood Saw")` |
| `has_text` khớp chuỗi con | `filter(has_text="Pliers")` khớp cả "Combination Pliers" | Dùng `product_card(name)` trong HomePage: so khớp nguyên tên bằng regex |
| Tìm kiếm ngay khi vừa mở trang | Đọc ra danh sách trang chủ thay vì kết quả tìm kiếm, nhất là khi chạy song song | `HomePage.open()` chờ danh sách đầu tiên tải xong. Danh sách đó về muộn sẽ ghi đè kết quả tìm kiếm |
| Đọc ngay sau khi sắp xếp | Đọc ra thứ tự cũ | Chờ `sorting_completed` trước khi đọc |
| Đăng nhập sai bằng tài khoản dùng chung | Toolshop đếm số lần đăng nhập sai và có thể khoá tài khoản, cả lớp mất tài khoản mẫu | Test đăng nhập sai dùng email không tồn tại, ví dụ `nobody-here@example.com` |
| So số thực bằng `==` | `14.15 * 2` ra `28.299999...` | `pytest.approx(14.15 * 2)` |

## 7. Lỗi thường gặp

| Thông báo lỗi | Nguyên nhân |
|---|---|
| `NotImplementedError: B1.x` | Hàm trong `pages/` vẫn còn TODO |
| `strict mode violation ... resolved to N elements` | Locator khớp nhiều phần tử |
| `'NoneType' object has no attribute ...` | Action quên `return self` |
| `Timeout ... waiting for get_by_test_id("...")` | Sai tên data-test, hoặc đang ở sai trang |
| Giỏ hàng trống khi mở | Mở giỏ trước khi request thêm sản phẩm xong. Chờ badge đúng số lượng trước |

## 8. Tự kiểm tra

1. Vì sao locator đặt trong `__init__` mà không đặt trong từng hàm action?
2. Hành động nào nên trả về `self`, hành động nào trả về page object khác?
3. Đưa ra một ví dụ cụ thể trên Toolshop cho thấy vì sao page object không nên chứa assertion.
4. Toolshop đổi toàn bộ class CSS nhưng giữ nguyên data-test. Bộ test của nhóm em phải sửa bao nhiêu chỗ? Chứng minh bằng lệnh `grep`.
5. Vì sao `HomePage.open()` được phép chờ mà vẫn không vi phạm quy tắc "không assert trong page object"?

## 9. Liên hệ đồ án

- Mục 3.1 Page Object Model (1,0 điểm): mỗi trang một class, có BasePage, locator là thuộc tính, không assert trong page object, ưu tiên data-test.
- Câu vấn đáp 6 và 7 hỏi trực tiếp nội dung bài này.

## 10. Đọc thêm

- Page Object Model trong tài liệu Playwright: https://playwright.dev/python/docs/pom
- Locator: https://playwright.dev/python/docs/locators
- Mã nguồn Toolshop (xem data-test): https://github.com/testsmith-io/practice-software-testing
