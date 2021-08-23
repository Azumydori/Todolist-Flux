"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Account, Task
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code



@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/account', methods=['GET'])
def get_user():
    all_user = Account.get_all() 
    if all_user:
        return jsonify(all_user), 200

    return jsonify({'message': 'No account created, so make one!'}), 500


@app.route('/account/<int:id>', methods=['GET'])
def get_one_user(id):
    one_user = Account.get_by_id(id) 
    if one_user:
        return jsonify(one_user.to_dict()), 200

    return jsonify({'message': 'No account'}), 500


@app.route('/account/<int:id>/tasks', methods=['GET'])
def get_task(id):

    user_tasks = Task.get_task_by_user(id) 

    if not user_tasks:
        return jsonify({'message': 'No tasks yet'}), 200

    return jsonify(user_tasks), 200
    
@app.route('/user/<int:id>/tasks/<int:position>', methods=['GET'])
def get_specific_task(id, position):

    user_tasks = Task.get_task_by_user(id) 




    if not user_tasks:
        return jsonify({'message': 'Not specific task found, boo hoo'}), 200

    return jsonify(user_tasks), 200


@app.route('/account', methods=['POST'])
def create_user_task():

    nick = request.json.get('nick', None)
    
    if not (nick):
        return {'error': 'Missing info'}, 400

    user= Account(nick = nick)
    user.create()

    return jsonify(user.to_dict()),201

    
@app.route('/account/<int:id>/tasks', methods=['POST'])
def add_new_task(id):
    label = request.json.get('label', None)
    
    if not (label and id):
        return {'error': 'No enough info, baby'}, 400

    task= Task(label = label, account_id=id)
    task.add_new()

    return jsonify(task.to_dict()),201

    print("Incoming request", request_body)
    return jsonify(task)


@app.route('/account/<int:id>', methods = ['DELETE'])
def delete_account(id):
    account = Account.get_by_id(id)

    if account:
        account.delete()
        return jsonify(account.to_dict()), 200

    return jsonify({'msg' : 'Account not found sadface'}), 404


@app.route('/account/<int:id>', methods = ["PATCH"])
def update_account_by_id(id):
    account = Account.read_by_id(id)

    if not account:
        return jsonify({'msg': 'account not found...Yet'}), 404

    new_nick = request.json.get('nick', None)
    if new_nick and not Account.get_by_nick(new_nick):
        account.update(new_nick)
        return jsonify(account.to_dict()), 200

    return jsonify({'msg': 'Try another nick, please'}), 400
    

@app.route('/account/<int:id>/tasks/<int:position>', methods=['DELETE'])
def delete_user_task(id, position):
    
    task_to_delete = Task.get_one_task(position)

    if (task_to_delete):
        task_to_delete.delete()
        return jsonify(task_to_delete.to_dict()), 200

    return {'error': 'Access denied'}, 400
    

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)