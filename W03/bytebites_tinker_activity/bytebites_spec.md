# Candidate Classes

## Client Feature Request

We need to build the backend logic for the ByteBites app. The system needs to manage our customers, tracking their names and their past purchase history so the system can verify they are real users.

These customers need to browse specific food items (like a "Spicy Burger" or "Large Soda"), so we must track the name, price, category, and popularity rating for every item we sell.

We also need a way to manage the full collection of items — a digital list that holds all items and lets us filter by category such as "Drinks" or "Desserts".

Finally, when a user picks items, we need to group them into a single transaction. This transaction object should store the selected items and compute the total cost.

## UML Class Diagram

```plantuml
@startuml

class User {
    +int customer_id
    +String name
    +List~Order~ purchase_history
    +verify_customer() bool
    +add_to_history(order: Order) void
}

class MenuItem {
    +int item_id
    +String name
    +float price
    +String category
    +float popularity_rating
}

class Restaurant {
    +List~MenuItem~ items
    +add_item(item: MenuItem) void
    +remove_item(item_id: int) void
    +filter_by_category(category: String) List~MenuItem~
}

class Order {
    +int transaction_id
    +User user
    +List~MenuItem~ selected_items
    +add_item(item: MenuItem) void
    +compute_total() float
}

User "1" o--> "0..*" Order : purchase history
Order "*" --> "1" User : belongs to
Order "1" *--> "1..*" MenuItem : contains
Restaurant "1" o--> "0..*" MenuItem : holds

@enduml
```

