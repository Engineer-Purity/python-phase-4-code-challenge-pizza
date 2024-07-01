from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

# Import models
from server.models import Restaurant, Pizza, RestaurantPizza

# Index route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# RestaurantList Resource
class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

api.add_resource(RestaurantListResource, '/restaurants')

# Restaurant Resource
class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict()
        else:
            return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Restaurant not found"}, 404

api.add_resource(RestaurantResource, '/restaurants/<int:id>')

# PizzaList Resource
class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

api.add_resource(PizzaListResource, '/pizzas')

# RestaurantPizza Resource
class RestaurantPizzaResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('price', type=float, required=True, help='Price must be a float between 1 and 30')
        parser.add_argument('pizza_id', type=int, required=True, help='Pizza ID must be provided')
        parser.add_argument('restaurant_id', type=int, required=True, help='Restaurant ID must be provided')
        args = parser.parse_args()

        if not (1 <= args['price'] <= 30):
            return {"errors": ["Price must be between 1 and 30"]}, 400

        new_rp = RestaurantPizza(price=args['price'], pizza_id=args['pizza_id'], restaurant_id=args['restaurant_id'])
        db.session.add(new_rp)
        db.session.commit()

        return new_rp.to_dict(), 201

api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
