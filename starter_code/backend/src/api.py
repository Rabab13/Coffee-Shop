import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)

setup_db(app)
CORS(app)


# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN

# db_drop_and_create_all()

# ROUTES

# @TODO implement endpoint
#     GET /drinks
#  it should be a public endpoint
#  it should contain only the drink.short() data representation
#  returns status code 200 and json
# {"success": True, "drinks": drinks}
# where drinks is the list of drinks
#  or appropriate status code indicating reason for failure

@app.route("/drinks", methods=['GET'])
def get_drinks():
    try:
        # Query all drinks list
        querydrinks = db.session.query(Drink).all()
        querydrinks = []
        # Formating all drinks using through for loop.
        for drinks in querydrinks:
            drink.append(querydrinks.short())

        # Return drinks list from the database.
        return jsonify({
            'success': True,
            'drinks': querydrinks
        })
    # Abort not found if not exsit in the database.
    except Exception as E:
        print(E)
        abort(404)


# @TODO implement endpoint
#     GET /drinks-detail
#    it should require the 'get:drinks-detail' permission
#    it should contain the drink.long() data representation
#  returns status code 200 and json
#  {"success": True, "drinks": drinks}
#   where drinks is the list of drinks
#   or appropriate status code indicating reason for failure
@app.route("/drinks-detail", methods=["GET"])
@requires_auth(permission="get:drinks-detail")
def get_drinks_details(jwt_payload):
    try:
        # Query all drinks list
        querydrinks = db.session.query(Drink).all()
        drinks = []

        # Formating all drinks using through for loop.
        for drink in querydrinks:
            drinks.append(drink.long())

        print(drinks)
        # print(querydrinks)
        # Return drinks list from the database.
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    # Abort not found if not exsit in the database.
    except Exception as E:
        print(E)
        abort(404)


# @TODO implement endpoint
#     POST /drinks
#         it should create a new row in the drinks table
#         it should require the 'post:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json
#  {"success": True, "drinks": drink}
#  where drink an array containing only the newly created drink
#         or appropriate status code indicating reason for failure

@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def insert_new_drink(jwt_payload):
    # Get the data from the body in order to create new drinks
    getbody = request.get_json()
    if not getbody:
        abort(401)
    # Get title and recipe from body
    new_drinkt = getbody.get("title", None)
    new_reciper = getbody.get("recipe", None)
    if new_drinkt is None:
        abort(401)
    if new_reciper is None:
        abort(401)
    try:
        # Using dumps method to convert python object
        # to JSON string in recipe.
        newdrink = Drink(title=new_drinkt, recipe=json.dumps(new_reciper))
        newdrink.insert()
        # Formating the list of drinks as a long
        new_drinks = [newdrink.long()]

        return jsonify({
            "success": True,
            "drinks": new_drinks
        })
    except Exception as E:
        print(E)
        abort(422)


# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json
#    {"success": True, "drinks": drink}
#       where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure


@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink_id(jwt_payload, drink_id):
    # Get body's data
    getjson = request.get_json()
    # Query all drinks by id
    query_drinks = db.session.query(Drink).filter(
        Drink.id == drink_id).one_or_none()
    # Abort not found if not exist
    if query_drinks is None:
        abort(401)
    getdrinktitle = getjson.get("title", None)
    getdrinkrecipe = getjson.get("recipe", None)
    try:
        # Update drink
        # Using dumps method to convert python object
        #  to JSON string in recipe.
        query_drinks.title = getdrinktitle
        query_drinks.recipe = json.dumps(getdrinkrecipe)
        query_drinks.update()
        updated = [query_drinks.long()]

        return jsonify({
            "success": True,
            "drinks": updated
        })

    except Exception as E:
        print(E)
        abort(422)


# @TODO implement endpoint
#     DELETE /drinks/<id>
#   where <id> is the existing model id
#    it should respond with a 404 error if <id> is not found
#   it should delete the corresponding row for <id>
#   it should require the 'delete:drinks' permission
#   returns status code 200 and json {"success": True, "delete": id}
#  where id is the id of the deleted record
#  or appropriate status code indicating reason for failure

@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink_id(jwt_payload, drink_id):
    # Get body's data
    getjson = request.get_json()
    # Query all drinks by id
    query_drinks = db.session.query(Drink).filter(
        Drink.id == drink_id).one_or_none()
    # Abort not found if not exist
    if query_drinks is None:
        abort(401)
    try:
        # Delete selected drink
        query_drinks.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })

    except Exception as E:
        print(E)
        abort(422)


# Error Handling

# Example error handling for unprocessable entity


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# @TODO implement error handlers using the
#  @app.errorhandler(error) decorator
#     each error handler should return (with approprate messages):
#              jsonify({
#                     "success": False,
#                     "error": 404,
#                     "message": "resource not found"
#                     }), 404


# @TODO implement error handler for 404
#     error handler should conform to general task above


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'massage': 'Not found'
    }), 404


# @TODO implement error handler for AuthError
#     error handler should conform to general task above

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'massage': 'unauthorized'
    }), 401


@app.errorhandler(503)
def Service_Unavailable(error):
    return jsonify({
        'success': False,
        'error': 503,
        'massage': 'Service Unavailable'
    }), 503


@app.errorhandler(500)
def Internal_Server_Error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'massage': 'Internal Server Error'
    }), 500

@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 403,
        'massage': 'Forbidden'
    }), 403

@app.errorhandler(400)
def Bad_Request (error):
    return jsonify({
        'success': False,
        'error': 400,
        'massage': 'Bad Request'
    }), 400




if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=False)
