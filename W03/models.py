# models.py — ByteBites Backend Classes
#
# Four classes based on bytebites_design.md:
#
# 1. Customer   — App user with a name and purchase history for verification.
# 2. MenuItem   — A food/drink item with name, price, category, and popularity rating.
# 3. Menu       — Collection of MenuItems with category filtering.
# 4. Order      — Transaction grouping selected MenuItems with total computation.


class MenuItem:
    """A single food or drink item sold by ByteBites."""

    def __init__(self, name, price, category, popularity_rating):
        self._name = name
        self._price = price
        self._category = category
        self._popularity_rating = popularity_rating

    def get_name(self):
        return self._name

    def get_price(self):
        return self._price

    def get_category(self):
        return self._category

    def get_popularity_rating(self):
        return self._popularity_rating


class Menu:
    """A collection of MenuItems with category filtering."""

    def __init__(self):
        self._items = []

    def add_item(self, item):
        self._items.append(item)

    def remove_item(self, item):
        self._items.remove(item)

    def filter_by_category(self, category):
        return [item for item in self._items if item.get_category() == category]

    def sort_by_price(self, ascending=True):
        """Return items sorted by price."""
        return sorted(self._items, key=lambda item: item.get_price(), reverse=not ascending)

    def sort_by_popularity(self):
        """Return items sorted by popularity rating, highest first."""
        return sorted(self._items, key=lambda item: item.get_popularity_rating(), reverse=True)

    def get_all_items(self):
        return list(self._items)


class Order:
    """A transaction grouping selected MenuItems with total computation."""

    def __init__(self):
        self._selected_items = []

    def add_item(self, item):
        self._selected_items.append(item)

    def remove_item(self, item):
        self._selected_items.remove(item)

    def get_items(self):
        return list(self._selected_items)

    def compute_total(self):
        return sum(item.get_price() for item in self._selected_items)


class Customer:
    """An app user with a name and purchase history for verification."""

    def __init__(self, name):
        self._name = name
        self._purchase_history = []

    def get_name(self):
        return self._name

    def get_purchase_history(self):
        return list(self._purchase_history)

    def add_order(self, order):
        self._purchase_history.append(order)

    def is_verified(self):
        return len(self._purchase_history) > 0
