import csv
from App.controllers.admin import update_student
from App.controllers.review import downvote, upvote
from App.controllers.staff import create_review
from App.controllers.user import get_student
from App.views.index import generate_random_contact_number
import click, pytest, sys
from flask import Flask, jsonify
from flask.cli import with_appcontext, AppGroup
import random
import randomname
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, create_staff, add_student_information, get_all_users_json, get_all_users )
from App.views import (generate_random_contact_number)
from App.models import *

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  db.drop_all()
  db.create_all()
  admin= create_user('bob', 'boblast' , 'bobpass')
  for ID in range(50, 150): 
      student= add_student_information(admin, str(ID),
          randomname.get_name(), 
          randomname.get_name(), 
          random.choice(['Full-Time','Part-Time', 'Evening']),
          random.randint(2015, 2023)
      )
      db.session.add(student)
      db.session.commit()
  print("Database Intialized")
  return jsonify({'message': 'Database initialized'}),201

'''
User Commands
'''

#Use for testing the models. Would be deleted eventually as the controllers and views are updated
@app.cli.command("tm", help="Testing models")
def test():
    db.drop_all()
    db.create_all()
    student= Student("1234" , "sally", "trim", "full-time", 2020)
    s1= create_staff("55", "Jen", "Jlast", "pass", "email", 2010)
    s2= create_staff("54", "Sen", "Shin", "pass2", "email", 2021)
    s3= create_staff("57", "Sally", "Blue", "pass3", "email", 2014)
    s4= create_staff("59", "Rui", "Pear", "pass4", "email", 2000)
    s5= create_staff("70", "Ren", "Lue", "pass5", "email", 2017)
    r=s1.createReview(student, True, "Positive")
    upvote(r.ID, s2)
    downvote(r.ID, s3)
    upvote(r.ID, s5)
    upvote(r.ID, s4)
    student2= Student("233", "Luis", "Thompson", "full-time", 2021)
    r2= s2.createReview(student2, True, "Another positive")
    upvote(r2.ID, s4)
    print(student.to_json())
    print("Rankings: \n", s1.getStudentRankings())
    admin= create_user("A1", "f", "l")
    
    studenttt= Student("100" , "sally", "trim", "full-time", 2020)
    s2=  Student("200" , "sally", "trim", "full-time", 2020)
    db.session.add(studenttt)
    db.session.add(s2)
    db.session.commit()
    # Read the content of the file
    with open("uploads/updateTest.csv", 'r') as fp:
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
                    student_updated=update_student(admin=admin, student=student, field_to_update=row['field_for_update'], new_value=row['new_value'])
            else: 
                student_updated=update_student(admin=admin,student=student, field_to_update=row['field_for_update'],new_value=row['new_value'])
            
            if not student_updated:
                return jsonify({'error': f"ID already exists {row['ID']}"}), 400
            print(student_updated.to_json())
    return jsonify({"message": "Students information updated successfully"}), 200

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("firstname", default="rob")
@click.argument("password", default="robpass")
def create_user_command(firstname, password):
    create_user(firstname, password)
    print(f'{firstname} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)