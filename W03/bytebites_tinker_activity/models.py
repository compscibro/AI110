# ByteBites Data Models
# User       - Customer with name, ID, and order history. Verifies real users.
# MenuItem   - Food item with name, price, category, and popularity rating.
# Restaurant - Collection of MenuItems. Supports filtering and removal.
# Order      - Groups MenuItems into a transaction. Computes total cost.


class MenuItem:
    """Represents a food item available in the restaurant menu."""

    def __init__(
        self, item_id: int, name: str, price: float, category: str, popularity_rating: float
    ):
        """
        Initialize a MenuItem.

        Args:
            item_id: Unique identifier for the item.
            name: Display name of the item (e.g. 'Spicy Burger').
            price: Cost of the item in dollars.
            category: Menu category the item belongs to (e.g. 'Drinks', 'Desserts').
            popularity_rating: Numeric rating reflecting how popular the item is.
        """
        self.item_id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.popularity_rating = popularity_rating


class User:
    """Represents a customer who can place orders in the app."""

    def __init__(self, customer_id: int, name: str):
        """
        Initialize a User with an empty purchase history.

        Args:
            customer_id: Unique identifier for the customer.
            name: Full name of the customer.
        """
        self.customer_id = customer_id
        self.name = name
        self.purchase_history = []  # List of past Orders placed by this user

    def verify_customer(self) -> bool:
        """
        Check whether this user is a real, active customer.

        A user is considered verified if they have a valid ID,
        a non-empty name, and at least one past order on record.

        Returns:
            True if the user is verified, False otherwise.
        """
        return (
            self.customer_id > 0
            and bool(self.name)
            and len(self.purchase_history) > 0
        )

    def add_to_history(self, order: "Order") -> None:
        """
        Add a completed order to the user's purchase history.

        Args:
            order: The Order to record.
        """
        self.purchase_history.append(order)


class Order:
    """Represents a single transaction grouping selected MenuItems for a User."""

    def __init__(self, transaction_id: int, user: User):
        """
        Initialize an Order with an empty item list.

        Args:
            transaction_id: Unique identifier for this transaction.
            user: The User placing the order.
        """
        self.transaction_id = transaction_id
        self.user = user
        self.selected_items = []  # MenuItems added to this order

    def add_item(self, item: MenuItem) -> None:
        """
        Add a MenuItem to this order.

        Args:
            item: The MenuItem to add.
        """
        self.selected_items.append(item)

    def compute_total(self) -> float:
        """
        Calculate the total cost of all items in the order.

        Returns:
            The sum of item prices, rounded to 2 decimal places.
        """
        return round(sum(item.price for item in self.selected_items), 2)


class Restaurant:
    """Manages the full collection of MenuItems available to customers."""

    def __init__(self):
        """Initialize a Restaurant with an empty menu."""
        self.items = []  # All MenuItems currently on the menu

    def add_item(self, item: MenuItem) -> None:
        """
        Add a MenuItem to the menu.

        Args:
            item: The MenuItem to add.
        """
        self.items.append(item)

    def remove_item(self, item_id: int) -> None:
        """
        Remove a MenuItem from the menu by its ID.

        If no item with the given ID exists, the menu is unchanged.

        Args:
            item_id: The ID of the item to remove.
        """
        self.items = [item for item in self.items if item.item_id != item_id]

    def filter_by_category(self, category: str) -> list[MenuItem]:
        """
        Return all menu items belonging to a given category.

        Args:
            category: The category to filter by (e.g. 'Drinks').

        Returns:
            A list of MenuItems in that category. Returns an empty list if none found.
        """
        return [item for item in self.items if item.category == category]


def demo_menu_item():
    """Create sample MenuItems and print their attributes."""
    burger = MenuItem(1, 'Spicy Burger', 9.99, 'Burgers', 4.5)
    soda = MenuItem(2, 'Large Soda', 2.49, 'Drinks', 3.8)
    cake = MenuItem(3, 'Choco Cake', 4.99, 'Desserts', 4.9)

    print(burger.item_id)           # 1
    print(burger.name)              # Spicy Burger
    print(burger.price)             # 9.99
    print(burger.category)          # Burgers
    print(burger.popularity_rating) # 4.5

    print(soda.item_id)             # 2
    print(soda.name)                # Large Soda
    print(soda.category)            # Drinks

    print(cake.item_id)             # 3
    print(cake.name)                # Choco Cake
    print(cake.category)            # Desserts

    return burger, soda, cake


def demo_user_and_order(burger, soda):
    """Create a sample User and Order, then print their attributes."""
    user = User(1, 'Alice')
    print(user.customer_id)         # 1
    print(user.name)                # Alice
    print(user.purchase_history)    # []
    print(user.verify_customer())   # False (no history yet)

    order = Order(101, user)
    order.add_item(burger)
    order.add_item(soda)
    print(order.transaction_id)                     # 101
    print(order.user.name)                          # Alice
    print([i.name for i in order.selected_items])   # ['Spicy Burger', 'Large Soda']
    print(order.compute_total())                    # 12.48

    # Add the order to history and re-verify
    user.add_to_history(order)
    print(len(user.purchase_history))               # 1
    print(user.verify_customer())                   # True


def demo_restaurant(burger, soda, cake):
    """Create a sample Restaurant, add items, filter, and remove."""
    menu = Restaurant()
    menu.add_item(burger)
    menu.add_item(soda)
    menu.add_item(cake)
    print([i.name for i in menu.items])                         # ['Spicy Burger', 'Large Soda', 'Choco Cake']
    print([i.name for i in menu.filter_by_category('Drinks')])  # ['Large Soda']
    menu.remove_item(1)
    print([i.name for i in menu.items])                         # ['Large Soda', 'Choco Cake']


if __name__ == "__main__":
    burger, soda, cake = demo_menu_item()
    demo_user_and_order(burger, soda)
    demo_restaurant(burger, soda, cake)
