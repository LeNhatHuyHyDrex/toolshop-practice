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
