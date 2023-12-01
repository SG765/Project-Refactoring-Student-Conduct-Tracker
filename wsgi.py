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
  '''for ID in range(50, 150): 
      student= create_student(admin, str(ID),
          randomname.get_name(), 
          randomname.get_name(), 
          random.choice(['Full-Time','Part-Time', 'Evening']),
          str(random.randint(2010, 2020))
      )
      db.session.add(student)
      db.session.commit()'''

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
    s1= Staff("55", "Jen", "Jlast", "pass", "email", 13)
    s2= Staff("54", "Sen", "Shin", "pass2", "email", 1)
    s3= Staff("57", "Sally", "Blue", "pass3", "email", 10)
    s4= Staff("59", "Rui", "Pear", "pass4", "email", 18)
    s5= Staff("70", "Ren", "Lue", "pass5", "email", 13)
    r=s1.createReview(student, True, "Positive")
    r.upvoteReview(s2)
    r.downvoteReview(s3)
    r.upvoteReview(s4)
    r.upvoteReview(s5)

    student2= Student("233", "Luis", "Thompson", "full-time", 2021)
    r2= s2.createReview(student2, True, "Another positive")
    r2.upvoteReview(s4)

    print(student.to_json())
    print(student2.to_json())
    print("Rankings: \n", s1.getStudentRankings())

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