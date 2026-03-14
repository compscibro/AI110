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
        +int customer_id
        +String name
        +List~Transaction~ purchase_history
        +verify_customer() bool
        +add_to_history(transaction: Transaction) None
    }

    class FoodItem {
        +int item_id
        +String name
        +float price
        +String category
        +float popularity_rating
    }

    class Menu {
        +List~FoodItem~ items
        +add_item(item: FoodItem) None
        +remove_item(item_id: int) None
        +filter_by_category(category: String) List~FoodItem~
    }

    class Transaction {
        +int transaction_id
        +Customer customer
        +List~FoodItem~ selected_items
        +add_item(item: FoodItem) None
        +compute_total() float
    }

    Customer "1" o-- "0..*" Transaction : purchase history
    Transaction "*" --> "1" Customer : belongs to
    Transaction "1" *-- "1..*" FoodItem : contains
    Menu "1" o-- "0..*" FoodItem : holds
```

