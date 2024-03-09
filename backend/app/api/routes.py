from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import boto3
from botocore.exceptions import ClientError
import uuid
from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix

from ..extensions import mongo
from ..utils.database import MongoDBUserCollection


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/upload_recipe', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    # Check if the post request has the neccesary recipe data
    if 'name' not in data:
        return jsonify({'message': 'No name'}), 400
    if 'recipe' not in data:
        return jsonify({'message': 'No recipe'}), 400
    if 'creator_id' not in data:
        return jsonify({'message': 'No creator'}), 400
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    #upload file to s3
    if file and allowed_file(file.filename):
        try:
            filename = upload_photo_to_s3(file)
        except ClientError as e:
            return jsonify({'message': 'Error uploading photo to s3 - ' + e}), 400
    
    db = mongo.cx['savor']
    recipe_collection = db['recipes']
    name = data.get('name')
    recipe = data.get('recipe')
    creator_id = data.get('creator_id')
    photo_filename = filename
    recipe_id = str(uuid.uuid4())

    result = recipe_collection.insert_one({"id": recipe_id,
                                           "name": name,
                                           "recipe": recipe,
                                           "photo_filename": photo_filename,
                                           "creator_id": creator_id})
    
    return jsonify({"message": "Recipe successfully created"}), 201


def upload_photo_to_s3(file):
    s3 = boto3.client('s3')
    filename = secure_filename(file.filename)
    try:
        s3.upload_fileobj(file, S3_BUCKET, filename)

    except ClientError as e:
        print("Error uploading photo:", e)
        return e
    
    # after upload file to s3 bucket, return filename of the uploaded file
    return filename

@api.route('/add_recipe', methods=['POST'])
def add_recipe():
    data = request.get_json()
    # Check if the post request has the neccesary recipe data
    if 'user_id' not in data:
        return jsonify({'message': 'No user_id'}), 400
    if 'recipe_id' not in data:
        return jsonify({'message': 'No recipe_id'}), 400

    result = current_app.mongodb_user.add_recipe_to_user(data.get("user_id"), data.get("recipe_id"))

    return jsonify({"message": "Recipe added to User successfully"}), 200

@api.route('/get_recipes', methods=['GET'])
def get_recipes():

    data = request.get_json()
    user_id = data.get('user_id')

    recipes = current_app.mongodb_user.get_recipes(user_id)

    return jsonify(recipes), 200

blueprint = Blueprint('api', __name__, url_prefix = '/api')
api = Api(blueprint, title='My API', version='1.0', description='A simple API')


ns = api.namespace('', description='User API')

signup_model = api.model('User_Signup', {
    'email': fields.String(required=True, description='The user email'),
    'username': fields.String(required=True, description='The user username'),
    'password': fields.String(required=True, description='The user password'),
})

login_model = api.model('User_Login', {
    'email': fields.String(required=True, description='The user email'),
    'password': fields.String(required=True, description='The user password'),
})
signup_response_model = api.model('SignupResponse', {
    'email': fields.String(description='User email'),
    'username': fields.String(description='User username'),
    'error': fields.String(description='Error message'),
})


@ns.route('/signup')
class Signup(Resource):
    @ns.expect(signup_model, validate=True)
    #@ns.marshal_with(signup_response_model)
    def post(self):
        # Your existing signup logic here
        data = request.get_json()
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        user_id = str(uuid.uuid4())

        hashed_password = generate_password_hash(password)
        result = current_app.mongodb_user.signup_user(email, username, password)
        if result is not None:
            return {"email": result["email"], "username": result["username"], "recipes": result['recipes'], "error": ""}, 200
        else:
            return {"email": "", "username": "", "error": "User failed to signup"}, 400

@ns.route('/login')
class Signup(Resource):
    @ns.expect(login_model, validate=True)
    #@ns.marshal_with(signup_response_model)
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        result = current_app.mongodb_user.login_user(email, password)
        if result is not None:
            return (
                {"email": result["email"], "username": result["username"], "recipes": result["recipes"],  "error": ""}, 200
            )
        else:
            return (
                {"email": "", "username": "", "error": "User failed to login"},
                400
            )



@ns.route('/search_username')
class UserSearch(Resource):
    @ns.doc('search_username')
    @ns.expect(ns.parser().add_argument('username', type=str, required=False, help='Username query', location='args'))
    def get(self):
        args = request.args
        query = args.get("username", "")
        users= current_app.mongodb_user.search_usernames(query)
        user_list = [] 
        for user in users:
            user_data = {
                'email': user['email'],
                'username': user['username'],
                # Ensure recipes data is structured as a list of strings; adjust as necessary
                'recipes': user.get('recipes', [])
            }
            user_list.append(user_data)

        return {'users': user_list}
    

# api = Blueprint("api", __name__)

# UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../../uploads")
# ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)


# def allowed_file(filename):
#     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# @api.route("/upload", methods=["POST"])
# def upload_file():
#     # Check if the post request has the file part
#     if "file" not in request.files:
#         return jsonify({"message": "No file part"}), 400
#     file = request.files["file"]
#     # If the user does not select a file, the browser submits an
#     # empty file without a filename.
#     if file.filename == "":
#         return jsonify({"message": "No selected file"}), 400
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(UPLOAD_FOLDER, filename))
#         return jsonify({"message": "File successfully uploaded"}), 200


# @api.route("/signup", methods=["POST"])
# def signup():

#     data = request.get_json()
#     email = data.get("email")
#     username = data.get("username")
#     password = data.get("password")
#     user_id = str(uuid.uuid4())

#     hashed_password = generate_password_hash(password)
#     result = current_app.mongodb_user.signup_user(email, username, password)

#     if result is not None:
#         return (
#             jsonify(
#                 {"email": result["email"], "username": result["username"], "error": ""}
#             ),
#             200,
#         )
#     else:
#         return (
#             jsonify({"email": "", "username": "", "error": "User failed to signup"}),
#             400,
#         )


# @api.route("/login", methods=["POST"])
# def login():
#     data = request.get_json()
#     email = data.get("email")
#     password = data.get("password")

#     result = current_app.mongodb_user.login_user(email, password)
#     if result is not None:
#         return (
#             jsonify(
#                 {"email": result["email"], "username": result["username"], "error": ""}
#             ),
#             200,
#         )
#     else:
#         return (
#             jsonify({"email": "", "username": "", "error": "User failed to login"}),
#             400,
#         )


# @api.route("/search_user", methods=["GET"])
# def search_user():
#     query = request.args.get("user", "")
#     username_list = current_app.mongodb_user.search_usernames(query)
#     result = {"usernames": username_list}
#     return jsonify(result), 200
