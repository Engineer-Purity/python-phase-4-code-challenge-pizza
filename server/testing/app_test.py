# test_app.py

import pytest
from app import app, db
from models import Restaurant, Pizza, RestaurantPizza
from seed import seed_database  # Assuming a function to seed the database

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a separate in-memory database for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            seed_database()  # Seed the test database with sample data
        yield client
        db.session.remove()
        db.drop_all()

# Define the seed_database function in seed.py to populate test data
def seed_database():
    r1 = Restaurant(name="Karen's Pizza Shack", address="address1")
    r2 = Restaurant(name="Sanjay's Pizza", address="address2")
    r3 = Restaurant(name="Kiki's Pizza", address="address3")

    p1 = Pizza(name="Emma", ingredients="Dough, Tomato Sauce, Cheese")
    p2 = Pizza(name="Geri", ingredients="Dough, Tomato Sauce, Cheese, Pepperoni")
    p3 = Pizza(name="Melanie", ingredients="Dough, Sauce, Ricotta, Red peppers, Mustard")

    db.session.add_all([r1, r2, r3, p1, p2, p3])
    db.session.commit()

    rp1 = RestaurantPizza(price=1, restaurant_id=r1.id, pizza_id=p1.id)
    rp2 = RestaurantPizza(price=2, restaurant_id=r2.id, pizza_id=p2.id)
    rp3 = RestaurantPizza(price=3, restaurant_id=r3.id, pizza_id=p3.id)

    db.session.add_all([rp1, rp2, rp3])
    db.session.commit()

# Test Cases
def test_get_restaurants(client):
    response = client.get('/restaurants')
    assert response.status_code == 200
    assert len(response.json) == 3

def test_get_restaurant_by_id(client):
    response = client.get('/restaurants/1')
    assert response.status_code == 200
    assert response.json['id'] == 1

    response = client.get('/restaurants/999')
    assert response.status_code == 404

def test_delete_restaurant(client):
    response = client.delete('/restaurants/1')
    assert response.status_code == 204

    response = client.get('/restaurants/1')
    assert response.status_code == 404

def test_get_pizzas(client):
    response = client.get('/pizzas')
    assert response.status_code == 200
    assert len(response.json) == 3

def test_create_restaurant_pizza(client):
    data = {
        "price": 10,
        "restaurant_id": 1,
        "pizza_id": 1
    }
    response = client.post('/restaurant_pizzas', json=data)
    assert response.status_code == 201
    assert response.json['price'] == 10
    assert response.json['restaurant_id'] == 1
    assert response.json['pizza_id'] == 1
