# ByteBites Data Models
#
# User        - Represents a customer. Stores their name, ID, and order history.
#               Includes verification to confirm they are a real user.
# MenuItem    - Represents a food item on the menu. Tracks name, price,
#               category (e.g. "Drinks"), and popularity rating.
# Restaurant  - Holds the full collection of MenuItems. Supports adding,
#               removing, and filtering items by category.
# Order       - Groups selected MenuItems into a single transaction for a User.
#               Computes the total cost of all selected items.
