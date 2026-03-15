import pytest
from models import MenuItem, User, Order, Restaurant


# ---------------------------------------------------------------------------
# Fixtures — shared sample data reused across tests
# ---------------------------------------------------------------------------

@pytest.fixture
def items():
    """Provide a small set of MenuItems covering multiple categories and prices."""
    burger = MenuItem(1, "Spicy Burger", 9.99, "Burgers",  4.5)
    soda   = MenuItem(2, "Large Soda",   2.49, "Drinks",   3.8)
    cake   = MenuItem(3, "Choco Cake",   4.99, "Desserts", 4.9)
    water  = MenuItem(4, "Still Water",  1.00, "Drinks",   3.0)
    return burger, soda, cake, water


# ---------------------------------------------------------------------------
# Order — compute_total
# ---------------------------------------------------------------------------

def test_order_total_with_multiple_items(items):
    """Adding a burger ($9.99) and a soda ($2.49) produces a total of $12.48."""
    burger, soda, *_ = items
    user  = User(1, "Alice")
    order = Order(101, user)
    order.add_item(burger)
    order.add_item(soda)
    assert order.compute_total() == 12.48


def test_order_total_is_zero_when_empty():
    """An order with no items should return a total of $0.00."""
    user  = User(1, "Alice")
    order = Order(101, user)
    assert order.compute_total() == 0.0


def test_order_total_with_single_item(items):
    """An order containing exactly one item equals that item's price."""
    burger, *_ = items
    user  = User(1, "Alice")
    order = Order(101, user)
    order.add_item(burger)
    assert order.compute_total() == 9.99


# ---------------------------------------------------------------------------
# User — verify_customer & total_spent
# ---------------------------------------------------------------------------

def test_new_user_is_not_verified():
    """A brand-new user with no purchase history should not be verified."""
    user = User(1, "Alice")
    assert user.verify_customer() is False


def test_user_with_invalid_id_is_not_verified():
    """A user with customer_id of 0 is not verified, even with a valid name."""
    user = User(0, "Alice")
    assert user.verify_customer() is False


def test_user_with_empty_name_is_not_verified():
    """A user with an empty name string is not verified."""
    user = User(1, "")
    assert user.verify_customer() is False


def test_user_is_verified_after_adding_order(items):
    """A user becomes verified once they have at least one completed order."""
    burger, *_ = items
    user  = User(1, "Alice")
    order = Order(101, user)
    order.add_item(burger)
    user.add_to_history(order)
    assert user.verify_customer() is True


def test_user_total_spent_sums_all_orders(items):
    """total_spent returns the combined cost of every order in purchase history."""
    burger, soda, cake, *_ = items
    user = User(1, "Alice")

    order1 = Order(101, user)
    order1.add_item(burger)   # $9.99

    order2 = Order(102, user)
    order2.add_item(soda)     # $2.49
    order2.add_item(cake)     # $4.99

    user.add_to_history(order1)
    user.add_to_history(order2)

    assert user.total_spent() == 17.47


def test_user_total_spent_is_zero_with_no_history():
    """A user with no orders should report $0.00 total spent."""
    user = User(1, "Alice")
    assert user.total_spent() == 0.0


# ---------------------------------------------------------------------------
# Restaurant — filter_by_category
# ---------------------------------------------------------------------------

def test_filter_by_category_returns_matching_items(items):
    """Filtering by 'Drinks' returns only the items in that category."""
    burger, soda, cake, water = items
    menu = Restaurant()
    for item in (burger, soda, cake, water):
        menu.add_item(item)

    drinks = menu.filter_by_category("Drinks")
    assert len(drinks) == 2
    assert all(item.category == "Drinks" for item in drinks)


def test_filter_by_category_returns_empty_for_unknown_category(items):
    """Filtering by a category that doesn't exist returns an empty list."""
    burger, *_ = items
    menu = Restaurant()
    menu.add_item(burger)
    assert menu.filter_by_category("Pizza") == []


# ---------------------------------------------------------------------------
# Restaurant — filter_by_price_range
# ---------------------------------------------------------------------------

def test_filter_by_price_range_includes_boundary_values(items):
    """Items priced exactly at min or max of the range are included."""
    burger, soda, cake, water = items
    menu = Restaurant()
    for item in (burger, soda, cake, water):
        menu.add_item(item)

    result = menu.filter_by_price_range(1.00, 4.99)
    names = {item.name for item in result}
    assert "Still Water"  in names          # $1.00 — lower boundary
    assert "Choco Cake"   in names          # $4.99 — upper boundary
    assert "Spicy Burger" not in names      # $9.99 — above range


def test_filter_by_price_range_returns_empty_when_none_qualify(items):
    """No items in the menu priced within the range returns an empty list."""
    burger, *_ = items
    menu = Restaurant()
    menu.add_item(burger)
    assert menu.filter_by_price_range(0.01, 0.99) == []


# ---------------------------------------------------------------------------
# Restaurant — sort_by_price & sort_by_popularity
# ---------------------------------------------------------------------------

def test_sort_by_price_ascending(items):
    """Items sorted ascending should start with the cheapest item."""
    menu = Restaurant()
    for item in items:
        menu.add_item(item)

    prices = [item.price for item in menu.sort_by_price()]
    assert prices == sorted(prices)


def test_sort_by_price_descending(items):
    """Items sorted descending should start with the most expensive item."""
    menu = Restaurant()
    for item in items:
        menu.add_item(item)

    prices = [item.price for item in menu.sort_by_price(reverse=True)]
    assert prices == sorted(prices, reverse=True)


def test_sort_by_popularity_descending(items):
    """Items sorted by popularity descending should start with the highest-rated item."""
    menu = Restaurant()
    for item in items:
        menu.add_item(item)

    ratings = [item.popularity_rating for item in menu.sort_by_popularity(reverse=True)]
    assert ratings == sorted(ratings, reverse=True)


def test_sort_does_not_mutate_original_menu(items):
    """Sorting returns a new list and leaves the restaurant's items unchanged."""
    burger, soda, *_ = items
    menu = Restaurant()
    menu.add_item(burger)
    menu.add_item(soda)

    original_order = [item.item_id for item in menu.items]
    menu.sort_by_price()
    assert [item.item_id for item in menu.items] == original_order


# ---------------------------------------------------------------------------
# Restaurant — remove_item
# ---------------------------------------------------------------------------

def test_remove_item_deletes_correct_item(items):
    """Removing an item by ID leaves all other items in the menu intact."""
    burger, soda, cake, *_ = items
    menu = Restaurant()
    for item in (burger, soda, cake):
        menu.add_item(item)

    menu.remove_item(1)  # remove burger
    ids = [item.item_id for item in menu.items]
    assert 1 not in ids
    assert 2 in ids
    assert 3 in ids


def test_remove_item_with_nonexistent_id_does_nothing(items):
    """Removing an ID that doesn't exist leaves the menu unchanged."""
    burger, *_ = items
    menu = Restaurant()
    menu.add_item(burger)

    menu.remove_item(999)
    assert len(menu.items) == 1
