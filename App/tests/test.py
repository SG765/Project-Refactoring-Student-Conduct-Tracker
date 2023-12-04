import json
import pytest
from flask import Flask, jsonify
from App.main import create_app
from App.database import create_db, db
from App.controllers import *
from App.models import Admin
from App.database import db, get_migrate
from flask_login import current_user, login_user

app = create_app()
migrate = get_migrate(app)
#run tests with "pytest App/tests/test.py" command in shell
# Fixture to create a test client for your Flask app
@pytest.fixture(autouse=True, scope="module")
def empty_db():
		app.config['TESTING'] = True
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
		with app.test_client() as client:
				create_db()
				yield client
		db.drop_all()

@pytest.fixture
def client():
		app.config['TESTING'] = True
		with app.test_client() as client:
				yield client

'''def test_upload(client):
        # Authenticate the admin user
		admin = create_user("bob", "boblast", "passs")   
		test_data = {
				'ID': admin.ID,
				'password': 'passs'
		}
		access_token = create_access_token(identity= admin.ID)
		# Include the access token in the headers for the subsequent request
		headers = {'Authorization': f'Bearer {access_token}'}
		with open('students.csv', 'rb') as file:
			response = client.post('/students', data={'file': (file, 'students.csv')}, headers=headers, content_type='multipart/form-data')

		assert response.status_code == 201
		
def test_update(client):
        # Authenticate the admin user
		admin = create_user("bob", "boblast", "passs")   
		test_data = {
				'ID': admin.ID,
				'password': 'passs'
		}
		studenttt= Student("100" , "sally", "trim", "full-time", 2020)
		student4= Student("200" , "sally", "trim", "full-time", 2020)
		db.session.add(studenttt, student4)
		db.session.commit()
		access_token = create_access_token(identity= admin.ID)
		# Include the access token in the headers for the subsequent request
		headers = {'Authorization': f'Bearer {access_token}'}
		with open('updateTest.csv', 'rb') as file:
			response = client.put('/students', data={'file': (file, 'updateTest.csv')}, headers=headers, content_type='multipart/form-data')

		assert response.status_code == 200'''

def test_init_route(client):
    # Send a POST request to the /init route
    response = client.post('/init')

    # Check if the response status code is 201 (Created)
    assert response.json == "{'message': 'Database Initialized'}"

# Test the create_staff_action route with the admin_required decorator
'''def test_create_staff_action(client):
		# Authenticate the admin user
		admin = create_user("bob", "boblast", "passs")   
		test_data = {
				'ID': admin.ID,
				'password': 'passs'
		}
		
		access_token = create_access_token(identity= admin.ID)

		# Include the access token in the headers for the subsequent request
		headers = {'Authorization': f'Bearer {access_token}'}

		# Define test data for creating a staff member
		test_data = {
				'firstname': 'John',
				'lastname': 'Doe',
				'password': 'password123',
				'staffID': '222',
				'email': 'john@example.com',
				'teachingExperience': 5
		}

		response = client.post('/user/create_staff', data=json.dumps(test_data), headers=headers, content_type='application/json')


		# Assuming a successful creation returns a 201 status code for an admin user
		assert response.status_code == 201

def test_login_staff(client):
  # Authenticate the admin user
  admin = create_user("bob", "boblast", "passs")   
  staff = create_staff("Lucy", "Heart", "pass", "534", "lucy@heart.com", 7) 
  # Define test data for staff login
  login_data = {
      'ID': '534',
      'password': 'pass',
  }

  response = client.post('/api/login', data=json.dumps(login_data), content_type='application/json')

  # Assuming a successful login returns a 200 status code
  assert response.status_code == 200




def test_create_student_action(client):
	# Authenticate the admin user
	admin = create_user("bob", "boblast", "passs")   
	test_data = {
			'ID': admin.ID,
			'password': 'passs'
	}

	access_token = create_access_token(identity= admin.ID)

	# Include the access token in the headers for the subsequent request
	headers = {'Authorization': f'Bearer {access_token}'}
	
	# Define test data for creating a student
	stu_data = {
			'firstname': 'Jim',
			'lastname': 'Lee',
			'password': 'pass123',
			'studentID': '12345',
			'contact': 'jim@school.com',
			'studentType': 'Full-Time',
			'yearOfStudy': 1
	}

	response = client.post('/user/create_student', data=json.dumps(stu_data), headers=headers, content_type='application/json')

	# Assuming a successful creation returns a 201 status code
	assert response.status_code == 201


# Test the update_student_action route
def test_update_student_action(client):
    # Authenticate the admin user
    admin = create_user("bob", "boblast", "passs")   
    access_token = create_access_token(identity= admin.ID)
  
    # Include the access token in the headers for the subsequent request
    headers = {'Authorization': f'Bearer {access_token}'}
  
    # Define test data for creating a student
    stu_data = {
        'firstname': 'Jim',
        'lastname': 'Lee',
        'password': 'pass123',
        'studentID': '1235',
        'contact': 'jim@school.com',
        'studentType': 'Full-Time',
        'yearOfStudy': 1
    }
  
    response = client.post('/user/create_student', data=json.dumps(stu_data), headers=headers, content_type='application/json')
  
    # Assuming a successful creation returns a 201 status code
    assert response.status_code == 201

    # Define test data for updating the student
    update_data = {
        'firstname': 'Jim',
        'lastname': 'Lee',
        'contact': 'jim@school.com',
        'studentType': 'Part-time',
        'yearOfStudy': 2
    }

    student_id = '1235'  #student ID created 

    response = client.put(f'/student/{student_id}/update', data=json.dumps(update_data), headers=headers, content_type='application/json')

    # successful update returns a 200 status code
    assert response.status_code == 200

def test_review_stuff(client):
  # Authenticate a staff user
  admin = create_user("bob", "boblast", "passs")
  staff = create_staff("Jon", "Den", "password", "staff123", "john@example.com", 5)
  staff_token = create_access_token(identity=staff.ID)

  # Include the access token in the headers for the subsequent request
  headers = {'Authorization': f'Bearer {staff_token}'}

  # Create a student for testing
  student = create_student(admin, "2", "Jim", "Lee", "pass123", "jim@school.com", "Full-time", 1)
  
  # Define test data for creating a review
  review_data = {
      'comment': 'Great student!',
      'isPositive': True
  }

  response = client.post(f'/student/{student.ID}/reviews', data=json.dumps(review_data), headers=headers, content_type='application/json')

  # Assuming a successful creation returns a 201 status code
  assert response.status_code == 201

  review = create_review(staff.ID, '2', True, "This is a great review")

  staff2 = create_staff( "Lia", "Su", "password", "14", "lsu@school.com", 10)
  staff2_token = create_access_token(identity=staff2.ID)
  header2 = {'Authorization': f'Bearer {staff2_token}'}

  response = client.post(f'/review/{review.ID}/upvote', headers=header2)
  assert response.status_code == 200

  response = client.post(f'/review/{review.ID}/downvote', headers=header2)
  assert response.status_code == 200

  # Attempt to edit a review
  edited_review_data = {
      'isPositive': False,
      'comment': 'This is an edited review'
  }

  
  response = client.put(f'/review/edit/{review.ID}', data=json.dumps(edited_review_data), headers={'Authorization': f'Bearer {staff_token}', 'Content-Type': 'application/json'})
  assert response.status_code == 200
  #extra assertion testing for success response
  response_data = json.loads(response.data)
  assert isinstance(response_data, list)  # Ensure it's a list

  # Check each dictionary in the list for 'message' key
  found_message = False
  for item in response_data:
      if 'message' in item and item['message'] == 'Review Edited':
          found_message = True
          break

  #save id before delete
  revID= review.ID
  # Delete the review
  response = client.delete(f'/review/delete/{review.ID}', headers=headers)

  # Assuming the review is successfully deleted, it should return a 200 status code
  assert response.status_code == 200

  # test get review iew the review and if review deleted
  response = client.get(f'/review/{revID}')

  # check if review successfully deleted
  assert response.status_code == 404
  
  

def test_search_students_action(client):
  # Authenticate a staff user
  admin = create_user("bob", "boblast", "passs")
  staff = create_staff("John", "Myn", "password", "staff3", "john@staff.com", 5)
  access_token = create_access_token(identity=staff.ID)

  # Include the access token in the headers for the subsequent request
  headers = {'Authorization': f'Bearer {access_token}'}

  # Define test data for searching students
  search_term= 'Jim'

  response = client.get(f'/students/search/{search_term}', headers=headers, content_type='application/json')
  # Assuming a successful search returns a 200 status code
  assert response.status_code == 200

  response = client.get('/rankings', headers=headers, content_type='application/json')

   #Assuming a successful search returns a 200 status code
  assert response.status_code == 200'''
