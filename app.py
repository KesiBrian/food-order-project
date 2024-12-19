from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()
engine = create_engine('sqlite:///food_ordering.db')  # SQLite database file
Session = sessionmaker(bind=engine)
session = Session()

# Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FoodItem(Base):
    __tablename__ = 'food_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='orders')
    total_price = Column(Float, nullable=False)

User.orders = relationship('Order', back_populates='user')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    food_item_id = Column(Integer, ForeignKey('food_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    food_item = relationship('FoodItem')

Order.items = relationship('OrderItem', back_populates='order')
OrderItem.order = relationship('Order', back_populates='items')

# Initialize database
Base.metadata.create_all(engine)

# Functions
def register_user(username, password):
    if session.query(User).filter_by(username=username).first():
        return "Username already exists."
    user = User(username=username)
    user.set_password(password)
    session.add(user)
    session.commit()
    return "User registered successfully."

def login_user(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        return "Login successful."
    return "Invalid username or password."

def add_food_item(name, price):
    food_item = FoodItem(name=name, price=price)
    session.add(food_item)
    session.commit()
    return f"Added food item: {name} (${price})."

def create_order(username, food_items):
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return "User not found."

    total_price = 0
    order = Order(user_id=user.id, total_price=0)
    session.add(order)
    session.commit()

    for item_id, quantity in food_items.items():
        food_item = session.query(FoodItem).get(item_id)
        if not food_item:
            return f"Food item with ID {item_id} not found."
        total_price += food_item.price * quantity
        order_item = OrderItem(order_id=order.id, food_item_id=item_id, quantity=quantity)
        session.add(order_item)

    order.total_price = total_price
    session.commit()
    return f"Order created successfully. Total price: ${total_price:.2f}."

def list_food_items():
    return session.query(FoodItem).all()

# Helper Functions for User Input
def get_user_input(prompt):
    return input(prompt)

def handle_user_input():
    while True:
        print("\n1. Register a user")
        print("2. Login")
        print("3. Add food item")
        print("4. Create an order")
        print("5. List food items")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            username = get_user_input("Enter username: ")
            password = get_user_input("Enter password: ")
            print(register_user(username, password))

        elif choice == '2':
            username = get_user_input("Enter username: ")
            password = get_user_input("Enter password: ")
            print(login_user(username, password))

        elif choice == '3':
            name = get_user_input("Enter food item name: ")
            price = float(get_user_input("Enter food item price: "))
            print(add_food_item(name, price))

        elif choice == '4':
            username = get_user_input("Enter username: ")
            food_items = {}
            while True:
                item_id = int(get_user_input("Enter food item ID (or 0 to stop): "))
                if item_id == 0:
                    break
                quantity = int(get_user_input(f"Enter quantity for item {item_id}: "))
                food_items[item_id] = quantity
            print(create_order(username, food_items))

        elif choice == '5':
            food_items = list_food_items()
            print("\nAvailable Food Items:")
            for item in food_items:
                print(f"{item.id}: {item.name} - ${item.price}")

        elif choice == '6':
            print("Goodbye!")
            break

# Start the program
if __name__ == '__main__':
    handle_user_input()
