from flask import Blueprint, jsonify, render_template, request, send_from_directory
from flask_jwt_extended import current_user as jwt_current_user
from flask_jwt_extended import jwt_required
from flask_login import current_user

from App.controllers import *

# Create a Blueprint for user views
user_views = Blueprint("user_views", __name__, template_folder='../templates')

# Route to get page of all users 
@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

# Route to get all users
@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

# Route to get all students
@user_views.route("/students", methods=["GET"])
def get_all_students_action():
    students = get_all_students()
    if students:
       return jsonify([student.to_json() for student in students]), 200
    else:
        return "No students found", 404


# Route to get all staff members
@user_views.route("/staff", methods=["GET"])
def get_all_staff_action():
    staff = get_all_staff()
    if staff:
        return jsonify([s.to_json() for s in staff]), 200
    else:
        return "No staff members found", 404


# Route to update a student's information
@user_views.route("/students/<string:id>", methods=["PUT"])
@jwt_required()
def update_student_action(id):
    if not jwt_current_user or not isinstance(jwt_current_user, Admin):
      return jsonify({"error" : "Unauthorized: You must be an admin to update students"}), 401

    student = get_student(str(id))
    if not student:
      return jsonify({"error": "Student with id {id} not found"}), 404

    data = request.json
    # Normalize the input field name by converting it to lowercase and replacing '-', '_', ' ' with ''
    input_field = data['field_for_update']
    input_field= input_field.lower().replace('-', '').replace('_', '').replace(' ', '')
    input_value = data['new_value']
    input_value= input_value.lower().replace('-', '').replace('_', '').replace(' ', '')
    
    if (input_field == "studenttype"):
        if input_value not in ["fulltime", "parttime", "evening", "graduated", "onleave"]:
          return jsonify({'error':f"{data['new_value']} was not a valid option"}), 400

    student_updated=update_student(admin=jwt_current_user, student=student, field_to_update=data['field_for_update'], new_value=data['new_value'])
    
    if not student_updated:
        return jsonify({'error': f"ID already exists data['ID']"}), 400

    if student_updated:
      return jsonify(student.to_json(), "Student information updated successfully"), 200
    else:
      return jsonify({"error": "Error updating student"}), 400 


@user_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_user_action():
    return jsonify({'message': f"username: {current_user.fistname}, id : {current_user.ID}, type: {current_user.user_type}"})
