import csv
import json
import os
from flask import Flask
from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from App.controllers.admin import add_student_information, update_student
from App.controllers.user import get_student

from App.models.admin import Admin

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from.index import index_views

from App.controllers import (
    create_user,
    jwt_authenticate,
    jwt_authenticate_admin,
)

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
         
@admin_views.route('/students', methods=['POST'])
@jwt_required()
def add_students():
  if not jwt_current_user or not isinstance(jwt_current_user, Admin):
      return 'Unauthorized', 401
  
  # Check if the POST request has a file
  if 'file' not in request.files:
      return jsonify({'error': 'No file selected'}), 400
  
  file = request.files['file']

  if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
  
  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    # Save the file to the upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Read the content of the file
    with open(file_path, 'r') as fp:
        file_content = csv.DictReader(fp)

        students_list = []  # List to store student information
        
        # Iterate over rows in the CSV file
        for row in file_content:
            student_type = row.get('studentType', '')

            # Normalize the input field name by converting it to lowercase and replacing '-', '_', ' ' with ''
            input_field = student_type.lower().replace('-', '').replace('_', '').replace(' ', '')

            if input_field not in ["fulltime", "parttime", "evening", "graduated", "onleave"]:
                return jsonify({'error': 'Invalid studentType in the file'}), 400

            student = add_student_information(admin= jwt_current_user, id=str(row['id']), firstname=row['firstname'], lastname=row['lastname'], studentType=row['studentType'], yearOfEnrollment=int(row['yearofEnrollment']))
            if not student:
                return jsonify({'error': f"ID already exists {row['ID']}"}), 400
            
            students_list.append(student)
    
    return jsonify({"message": "Student information uploaded successfully"}, [student.to_json() for student in students_list]), 201

#Route to batch update students via file upload
@admin_views.route('/students', methods=['PUT'])
def update_students():
    if not jwt_current_user or not isinstance(jwt_current_user, Admin):
      return 'Unauthorized', 401

     # Check if the PUT request has a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
  
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
    # Save the file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    # List of fields that can be updated for a student record
    allowed_fields = ["ID", "firstname", "lastname", "studenttype", "yearofenrollment"]
    students_list = []  # List to store student information

    with open(file_path, 'r') as fp:
        file_content = csv.DictReader(fp)
  

        for row in file_content:
            # Retrieve the student record based on student id
            studentid= row['id'].strip()
            student = get_student(studentID=str(studentid))

            if student is None:
                return jsonify({'error': f"Student not found"}), 400
            
            # Normalize the input field name by converting it to lowercase and replacing '-', '_', ' ' with ''
            input_field = row['field_for_update'].lower().replace('-', '').replace('_', '').replace(' ', '')
            input_value = row['new_value'].lower().replace('-', '').replace('_', '').replace(' ', '')
            
            if (input_field == "studenttype"):
                if input_value not in ["fulltime", "parttime", "evening", "graduated", "onleave"]:
                  return jsonify({'error':f"{row['new_value']} was not a valid option"}), 400
                else:
                    student_updated=update_student(admin=jwt_current_user, student=student, field_to_update=row['field_for_update'], new_value=row['new_value'])
                    if student_updated is None:
                        return jsonify({'error': f"Error Updating student type for student with ID {student.ID}"}), 400
                    
                    return jsonify({"message": "Students information updated successfully"}), 200
            else: 
                student_updated=update_student(admin=jwt_current_user,student=student, field_to_update=row['field_for_update'],new_value=row['new_value'])
                if not student_updated:
                    return jsonify({'error': f"Student with ID {row['ID']} not found"}), 400
            
            students_list.append(student)
    
    return jsonify({"message": "Students information updated successfully"}, [student.to_json() for student in students_list]), 200

