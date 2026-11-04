# B3.3 - write this feature yourself (Gherkin), then add "cart.feature" to scenarios(...) in test_b3_bdd.py
#
# Business rule to describe:
#   When a shopper adds a product with a quantity, the cart line price is unit price x quantity,
#   and the cart total is the sum of the line prices.
#
# Requirements:
#   - Feature with a 3-line user story (As a / I want / So that)
#   - One Scenario Outline with an Examples table of at least 2 rows: | product | quantity |
#     suggested rows: Combination Pliers / 1 and Claw Hammer / 3
#   - Steps speak business language ("I add it to the cart with quantity 3"),
#     never UI language ("I click the button with data-test add-to-cart").
