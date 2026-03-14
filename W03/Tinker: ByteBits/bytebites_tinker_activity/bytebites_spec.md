# Candidate Classes

## Client Feature Request

We need to build the backend logic for the ByteBites app. The system needs to manage our customers, tracking their names and their past purchase history so the system can verify they are real users.

These customers need to browse specific food items (like a "Spicy Burger" or "Large Soda"), so we must track the name, price, category, and popularity rating for every item we sell.

We also need a way to manage the full collection of items — a digital list that holds all items and lets us filter by category such as "Drinks" or "Desserts".

Finally, when a user picks items, we need to group them into a single transaction. This transaction object should store the selected items and compute the total cost.

## UML Class Diagram

```mermaid
classDiagram
    class Customer {
        +String name
        +List~Transaction~ purchase_history
        +verify_customer() bool
    }

    class FoodItem {
        +String name
        +float price
        +String category
        +float popularity_rating
    }

    class Menu {
        +List~FoodItem~ items
        +filter_by_category(category: String) List~FoodItem~
    }

    class Transaction {
        +List~FoodItem~ selected_items
        +Customer customer
        +compute_total() float
    }

    Customer "1" --> "0..*" Transaction : places
    Transaction "0..*" o-- "1..*" FoodItem : contains
    Menu "1" o-- "0..*" FoodItem : holds
```