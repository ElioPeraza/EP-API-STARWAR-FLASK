import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorites

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_user_favorites_by_id(id):
    all_favorites = Favorites.query.filter_by(id_user=id).all()
    favorites = list(map(lambda x: x.dict(), all_favorites))
    return jsonify(favorites), 200


@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    people = list(map(lambda x: x.dict(), all_people))
    return jsonify(people), 200

@app.route('/people/<int:id_people>', methods=['GET'])
def get_people_by_id(id_people):
    person = People.query.get(id_people)
    if person:
        return jsonify(person.dict()), 200
    return jsonify({"msg": "Person not found"}), 404

@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    planets = list(map(lambda x: x.dict(), all_planets))
    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.dict()), 200
    return jsonify({"msg": "Planet not found"}), 404

@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    users = list(map(lambda x: x.dict(), all_users))
    return jsonify(users), 200

@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_user_favorites(id):
    all_favorites = Favorites.query.filter_by(id_user=id).all()
    favorites = list(map(lambda x: x.dict(), all_favorites))
    return jsonify(favorites), 200

@app.route('/users/<int:id_user>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(id_user, planet_id):
    
    favorite_planet = Favorites.query.filter_by(id_user=id_user, id_planet=planet_id).first()
    if favorite_planet:
        return jsonify({"msg": "Planet is already a favorite"}), 400  
    
    favorite_planet = Favorites(id_user=id_user, id_planet=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()
    return jsonify(favorite_planet.dict()), 200


@app.route('/users/<int:id_user>/favorite/people/<int:id_people>', methods=['POST'])
def add_favorite_person(id_user, id_people):
   
    favorite_person = Favorites.query.filter_by(id_user=id_user, id_people=id_people).first()
    if favorite_person:
        return jsonify({"msg": "Person is already a favorite"}), 400  
    
    favorite_person = Favorites(id_user=id_user, id_people=id_people)
    db.session.add(favorite_person)
    db.session.commit()
    return jsonify(favorite_person.dict()), 200


@app.route('/users/<int:id_user>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(id_user, planet_id):
    favorite_planet = Favorites.query.filter_by(id_user=id_user, id_planet=planet_id).first()
    if favorite_planet:
        db.session.delete(favorite_planet)
        db.session.commit()
        return jsonify({"msg": "Favorite planet deleted"}), 200
    return jsonify({"msg": "Favorite planet not found"}), 404


@app.route('/users/<int:id_user>/favorite/people/<int:id_people>', methods=['DELETE'])
def delete_favorite_person(id_user, id_people):
    favorite_person = Favorites.query.filter_by(id_user=id_user, id_people=id_people).first()
    if favorite_person:
        db.session.delete(favorite_person)
        db.session.commit()
        return jsonify({"msg": "Favorite person deleted"}), 200
    return jsonify({"msg": "Favorite person not found"}), 404


#  nuevos planetas y personas
@app.route('/planets', methods=['POST'])
def add_planet():
    try:
        
        data = request.get_json()

        
        name = data.get('name')
        gravity = data.get('gravity')
        terrain = data.get('terrain')
        climate = data.get('climate')

        
        if not name or not gravity or not terrain or not climate:
            return jsonify({"msg": "Name, gravity, terrain, and climate are required"}), 400

      
        new_planet = Planet(name=name, gravity=gravity, terrain=terrain, climate=climate)

       
        db.session.add(new_planet)
        db.session.commit()

       
        return jsonify(new_planet.dict()), 201

    except Exception as e:
        db.session.rollback()  
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500


@app.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()  # Obtener los datos del body en formato JSON
    name = data.get('name')
    height = data.get('height')
    eye_color = data.get('eye_color')
    mass = data.get('mass')
    
    
    if not name or not height or not mass:
        return jsonify({"msg": "Name, height, and mass are required"}), 400
    
   
    new_person = People(name=name, height=height, eye_color=eye_color, mass=mass)
    
 
    db.session.add(new_person)
    db.session.commit()
    
    return jsonify(new_person.dict()), 201  


# actualizar planetas y personas
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.get_json()
    planet = Planet.query.get(planet_id)
    
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    
    
    name = data.get('name', planet.name)
    gravity = data.get('gravity', planet.gravity)
    terrain = data.get('terrain', planet.terrain)
    climate = data.get('climate', planet.climate)
    
    
    planet.name = name
    planet.gravity = gravity
    planet.terrain = terrain
    planet.climate = climate
    
    
    db.session.commit()
    
    return jsonify(planet.dict()), 200


@app.route('/people/<int:id_people>', methods=['PUT'])
def update_person(id_people):
    data = request.get_json()
    person = People.query.get(id_people)
    
    if not person:
        return jsonify({"msg": "Person not found"}), 404
    
    name = data.get('name', person.name)
    age = data.get('age', person.age)
    
    person.name = name
    person.age = age
    db.session.commit()
    
    return jsonify(person.dict()), 200

# eliminar planetas y personas
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    
    return jsonify({"msg": "Planet deleted"}), 200

@app.route('/people/<int:id_people>', methods=['DELETE'])
def delete_person(id_people):
    person = People.query.get(id_people)
    
    if not person:
        return jsonify({"msg": "Person not found"}), 404
    
    db.session.delete(person)
    db.session.commit()
    
    return jsonify({"msg": "Person deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
