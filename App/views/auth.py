from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from datetime import datetime, timedelta
from App.controllers.auth import jwt_authenticate_staff

from App.controllers.user import create_staff, get_admin, get_staff, get_student

from.index import index_views

from App.controllers import (
    create_user,
    jwt_authenticate,
    jwt_authenticate_admin,
    login 
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

@auth_views.route('/identify', methods=['GET'])
@login_required
def identify_page():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

# Route to create a new staff member
@auth_views.route("/signup", methods=["POST"])
def create_staff_action():
  #get data from the post request body 
  data = request.json
  
  #validate data
  if not data['staffID'] or not data['firstname'] or not data['lastname'] or not data['password'] or not data['email'] or not data['yearStartedTeaching']:
    return jsonify({"error": "Invalid request data"}), 400
	  
  email=data['email']	  
  email_status = email.endswith("@sta.uwi.edu")
  if email_status == False:
      return jsonify({"error": "Invalid email extension"}), 400	
	
  if get_student(data['staffID']) or get_staff(data['staffID']) or get_admin(data['staffID']):
    return jsonify({"error": f"A user already uses the ID {data['staffID']}"}), 400
  else:    
    staff = create_staff(data['staffID'], data['firstname'], data['lastname'], data['password'], data['email'], data['yearStartedTeaching'])
    if staff:
      return jsonify({"message": f"Staff created with ID {staff.ID}"}, staff.to_json()), 201
    else:
      return jsonify({"error": "Error creating staff"}), 400

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.json
    user = login(data['ID'], data['password'])
    if user:
        session['logged_in'] = True
        token = jwt_authenticate(data['ID'], data['password'])
        return 'user logged in!'
    return 'bad username or password given', 401
   

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
	data = request.json
	token = jwt_authenticate_staff(str(data['ID']), data['password'])
	if not token:
		return jsonify({"error":'invalid credentials'}), 400
	return jsonify(access_token=token)

@auth_views.route('/api/admin/login', methods=['POST'])
def admin_login_api():
  data = request.json
  token = jwt_authenticate_admin(str(data['ID']), data['password'])
  if not token:
    return jsonify({"error": 'invalid credentials'}), 400
  return jsonify(access_token=token)


@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user_action():
    return jsonify({'message': f"firstname: {jwt_current_user.firstname}, lastname: {jwt_current_user.lastname}, id : {jwt_current_user.ID}"})

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    logout_user()
    return redirect('/'), jsonify('logged out!')