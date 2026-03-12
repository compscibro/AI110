from models import MenuItem, Menu, Order, Customer


# ── MenuItem Tests ──

def test_menu_item_stores_attributes():
    """Verify MenuItem stores name, price, category, and popularity rating."""
    item = MenuItem("Spicy Burger", 8.99, "Entrees", 4.5)
    assert item.get_name() == "Spicy Burger"
    assert item.get_price() == 8.99
    assert item.get_category() == "Entrees"
    assert item.get_popularity_rating() == 4.5


# ── Menu Filtering Tests ──

def test_filter_by_category_returns_matching_items():
    """Filtering by 'Drinks' returns only drink items."""
    menu = Menu()
    soda = MenuItem("Large Soda", 2.49, "Drinks", 4.0)
    burger = MenuItem("Spicy Burger", 8.99, "Entrees", 4.5)
    water = MenuItem("Bottled Water", 1.99, "Drinks", 3.2)
    menu.add_item(soda)
    menu.add_item(burger)
    menu.add_item(water)

    drinks = menu.filter_by_category("Drinks")
    assert len(drinks) == 2
    names = [d.get_name() for d in drinks]
    assert "Large Soda" in names
    assert "Bottled Water" in names


def test_filter_by_category_returns_empty_when_no_match():
    """Filtering by a category with no items returns an empty list."""
    menu = Menu()
    menu.add_item(MenuItem("Spicy Burger", 8.99, "Entrees", 4.5))

    result = menu.filter_by_category("Desserts")
    assert result == []


# ── Menu Sorting Tests ──

def test_sort_by_price_ascending():
    """Sorting by price ascending returns cheapest item first."""
    menu = Menu()
    menu.add_item(MenuItem("Burger", 8.99, "Entrees", 4.5))
    menu.add_item(MenuItem("Water", 1.99, "Drinks", 3.2))
    menu.add_item(MenuItem("Cake", 5.99, "Desserts", 4.8))

    sorted_items = menu.sort_by_price(ascending=True)
    prices = [item.get_price() for item in sorted_items]
    assert prices == [1.99, 5.99, 8.99]


def test_sort_by_price_descending():
    """Sorting by price descending returns most expensive item first."""
    menu = Menu()
    menu.add_item(MenuItem("Burger", 8.99, "Entrees", 4.5))
    menu.add_item(MenuItem("Water", 1.99, "Drinks", 3.2))
    menu.add_item(MenuItem("Cake", 5.99, "Desserts", 4.8))

    sorted_items = menu.sort_by_price(ascending=False)
    prices = [item.get_price() for item in sorted_items]
    assert prices == [8.99, 5.99, 1.99]


def test_sort_by_popularity_highest_first():
    """Sorting by popularity returns the highest-rated item first."""
    menu = Menu()
    menu.add_item(MenuItem("Burger", 8.99, "Entrees", 4.5))
    menu.add_item(MenuItem("Cake", 5.99, "Desserts", 4.8))
    menu.add_item(MenuItem("Water", 1.99, "Drinks", 3.2))

    sorted_items = menu.sort_by_popularity()
    ratings = [item.get_popularity_rating() for item in sorted_items]
    assert ratings == [4.8, 4.5, 3.2]


# ── Order Tests ──

def test_order_total_with_multiple_items():
    """Order total equals the sum of all selected item prices."""
    order = Order()
    order.add_item(MenuItem("Burger", 10.00, "Entrees", 4.5))
    order.add_item(MenuItem("Soda", 5.00, "Drinks", 4.0))

    assert order.compute_total() == 15.00


def test_order_total_is_zero_when_empty():
    """An empty order should have a total of zero."""
    order = Order()
    assert order.compute_total() == 0


def test_order_remove_item():
    """Removing an item updates the total correctly."""
    burger = MenuItem("Burger", 10.00, "Entrees", 4.5)
    soda = MenuItem("Soda", 5.00, "Drinks", 4.0)
    order = Order()
    order.add_item(burger)
    order.add_item(soda)
    order.remove_item(soda)

    assert order.compute_total() == 10.00
    assert len(order.get_items()) == 1


# ── Customer Tests ──

def test_customer_not_verified_without_orders():
    """A new customer with no orders is not verified."""
    customer = Customer("Alice")
    assert customer.is_verified() is False


def test_customer_verified_after_order():
    """A customer becomes verified after placing an order."""
    customer = Customer("Alice")
    order = Order()
    order.add_item(MenuItem("Burger", 8.99, "Entrees", 4.5))
    customer.add_order(order)

    assert customer.is_verified() is True


def test_customer_purchase_history_tracks_orders():
    """Purchase history grows as orders are added."""
    customer = Customer("Bob")
    order1 = Order()
    order2 = Order()
    customer.add_order(order1)
    customer.add_order(order2)

    assert len(customer.get_purchase_history()) == 2
