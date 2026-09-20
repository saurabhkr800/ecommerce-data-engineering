from faker import Faker
import pandas as pd
import random
from datetime import datetime

fake = Faker("en_IN")

# Number of records
NUM_CUSTOMERS = 20_000
NUM_PRODUCTS = 2_000

# -----------------------------
# Generate Customers
# -----------------------------

customers = []

for i in range(NUM_CUSTOMERS):
    customers.append({
        "customer_name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "city": fake.city(),
        "state": fake.state(),
        "country": "India",
        "created_at": fake.date_time_between(
            start_date="-2y",
            end_date="now"
        ),
        "updated_at": datetime.now()
    })

customers_df = pd.DataFrame(customers)

customers_df.to_csv(
    "data/raw/customers.csv",
    index=False
)

print(f"Customers generated: {len(customers_df)}")


# -----------------------------
# Generate Products
# -----------------------------

categories = [
    "Beverages",
    "Grocery",
    "Personal Care",
    "Food",
    "Home Care"
]

brands = [
    "Tata",
    "Tata Tea",
    "Himalaya",
    "Nestle",
    "ITC",
    "Britannia"
]

products = []

for i in range(NUM_PRODUCTS):
    price = round(random.uniform(20, 2000), 2)
    cost = round(price * random.uniform(0.5, 0.8), 2)

    products.append({
        "product_name": fake.word().title(),
        "category": random.choice(categories),
        "brand": random.choice(brands),
        "price": price,
        "cost": cost,
        "created_at": fake.date_time_between(
            start_date="-2y",
            end_date="now"
        ),
        "updated_at": datetime.now()
    })

products_df = pd.DataFrame(products)

products_df.to_csv(
    "data/raw/products.csv",
    index=False
)

print(f"Products generated: {len(products_df)}")

# -----------------------------
# Generate Orders
# -----------------------------

NUM_ORDERS = 50_000

channels = [
    "E_COMMERCE",
    "MODERN_TRADE",
    "RETAIL"
]

order_statuses = [
    "CREATED",
    "CONFIRMED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED"
]

orders = []

for i in range(NUM_ORDERS):

    orders.append({
        "customer_id": random.randint(1, NUM_CUSTOMERS),
        "order_date": fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ),
        "channel": random.choice(channels),
        "order_status": random.choice(order_statuses),
        "total_amount": round(
            random.uniform(100, 10000),
            2
        ),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })

orders_df = pd.DataFrame(orders)

orders_df.to_csv(
    "data/raw/orders.csv",
    index=False
)

print(f"Orders generated: {len(orders_df)}")