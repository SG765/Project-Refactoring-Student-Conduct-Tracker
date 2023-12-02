from datetime import datetime
import os, tempfile, pytest, logging, unittest
from unittest.mock import patch
from werkzeug.security import check_password_hash, generate_password_hash
import random
from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Staff, Admin, Review
from App.controllers import (
    create_user,
    add_student_information,
    jwt_authenticate_admin,
    jwt_authenticate,
    get_student,
    get_staff,
    create_staff, 
    update_student,
    create_review, 
    edit_review, 
    delete_review, 
    get_review, 
    get_reviews_for_student, 
    get_reviews_by_staff, 
    upvote, 
    downvote,
    get_student_rankings, 
    search_students_searchTerm
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''

#run tests with "pytest App/tests/test_app.py" command in shell

class UserUnitTests(unittest.TestCase):

    def test_new_admin (self):
        newAdmin = Admin("Bob", "Boblast",  "bobpass")
        assert newAdmin.firstname == "Bob" and newAdmin.lastname == "Boblast"

    def test_new_staff (self):
        newStaff = Staff( "342", "Bob", "Charles", "bobpass", "bob.charles@staff.com", 2010)
        assert newStaff.firstname == "Bob" and newStaff.lastname == "Charles" and newStaff.check_password("bobpass") and newStaff.ID == "342" and newStaff.email == "bob.charles@staff.com" and newStaff.yearStartedTeaching == 2010

    def test_new_student (self):
        newStudent = Student( "813", "Joe", "Dune", "Full-Time", 2022)
        assert newStudent.ID == "813" and newStudent.firstname == "Joe" and newStudent.lastname == "Dune" and newStudent.studentType == "Full-Time" and newStudent.yearOfEnrollment == 2022

    def test_calculate_year_study(self):
        # Create a Student object
        student = Student("123", "John", "Doe", "Full-time", 2022)

       # Set the current date to a specific date (e.g., December 1st, 2023)
        specific_date = datetime(2023, 12, 1)
        year_of_study = student.calculate_year_study(current_date=specific_date)


        # Assert the expected result based on the mock date
        self.assertEqual(year_of_study, 2)
        
    def test_set_password(self): 
        newAdmin = Admin("Bob", "Boblast",  "bobpass")
        password = newAdmin.password
        assert newAdmin.set_password("tompass") != password and newAdmin.check_password != password

    def test_check_password(self): 
        newAdmin = Admin("Bob", "Boblast",  "bobpass")
        assert newAdmin.check_password("bobpass") != "bobpass"

    def test_admin_to_json(self): 
        newAdmin = Admin("Bob", "Boblast",  "bobpass")
        newAdmin_json = newAdmin.to_json()
        self.assertDictEqual(newAdmin_json, {"adminID":"A1", "firstname":"Bob", "lastname":"Boblast"})

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = Admin("bob", "boblast",  "bobpass")
        user_json = user.to_json()
        self.assertDictEqual(user_json, {"adminID":"A1", "firstname":"bob", "lastname":"boblast"})
    
    def test_hashed_password(self):
        password = "mypass"
        user = Admin("bob", "boblast",  password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = Admin("bob", "boblast",  password)
        assert user.check_password(password)

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    with app.test_client() as client:
        create_db()
        yield client
        db.session.remove()
    db.drop_all()

@pytest.fixture
def client():
		app.config['TESTING'] = True
		with app.test_client() as client:
				yield client

class UsersIntegrationTests(unittest.TestCase):
    def test_authenticate_admin(self): 
        newAdmin = create_user("bob", "boblast", "bobpass")
        token = jwt_authenticate_admin(newAdmin.ID, "bobpass")
        assert token is not None
    
    def test_create_student(self):
        newAdmin = create_user("rick", "rolast", "bobpass")
        newStudent = add_student_information(newAdmin, "813", "Joe", "Dune", "Full-Time", 2019)
        assert newAdmin.firstname == "rick" and newAdmin.lastname == "rolast"
        assert newStudent.ID == "813" 
        assert newStudent.firstname == "Joe" 
        assert newStudent.lastname == "Dune" 
        assert newStudent.studentType == "Full-Time" 
        assert newStudent.yearOfEnrollment == 2019

    def test_create_staff(self):
        newStaff = create_staff("342", "Bob", "Charles", "bobpass", "bob.charles@staff.com", 2010)
        assert newStaff.firstname == "Bob" 
        assert newStaff.lastname == "Charles" 
        assert newStaff.check_password("bobpass") 
        assert newStaff.ID == "342" 
        assert newStaff.email == "bob.charles@staff.com" 
        assert newStaff.yearStartedTeaching == 2010

    def test_search_students(self):
        staff = get_staff(342)
        assert search_students_searchTerm(staff, "Joe") is not None

    def test_authenticate_staff(self): 
        newStaff = create_staff("343", "Bobby", "Charls", "bobbpass", "bobby.charls@staff.com", 2010)
        token = jwt_authenticate(newStaff.ID, "bobbpass", Staff)
        assert newStaff is not None
        assert token is not None 
    
    def test_update_student(self): 
        newAdmin = create_user ("tom", "tomlast", "tompass")
        student = get_student("813") 
        oldFirstname = student.firstname
        oldLastname = student.lastname 
        oldStudentType = student.studentType
        oldYearOfEnrollment = student.yearOfEnrollment

        update_student(newAdmin, student.ID, "firstname", "tominton")
        update_student(newAdmin, student.ID, "lastname", "tomintonlast")
        update_student(newAdmin, student.ID, "studentType", "Part-Time")
        update_student(newAdmin, student.ID, "yearOfEnrollment", 2020)
                       
        assert student.firstname != oldFirstname and student.firstname == "tominton"
        assert student.lastname != oldLastname and student.lastname == "tomintonlast"
        assert student.studentType != oldStudentType and student.studentType == "Part-Time"
        assert student.yearOfEnrollment != oldYearOfEnrollment and student.yearOfEnrollment == 2020

    def test_create_review(self): 
        admin = create_user("rev", "revlast", "revpass")
        staff = create_staff("546", "Jon", "Den", "password", "john@example.com", 2015)
        student = add_student_information(admin, "2", "Jim", "Lee", "Full-time", 2021)
        review = create_review(staff.ID, student.ID, True, "This is a great review")
        assert admin and staff and student
        assert review.reviewerID == staff.ID
        assert review.studentID == student.ID 
        assert review.isPositive == True 
        assert review.comment == "This is a great review"

    def test_edit_review(self): 
        admin = create_user("grey", "graylast", "graypass")
        staff = create_staff("756", "Ben", "Gen", "password", "ben@example.com", 2017)
        student = add_student_information(admin, "456", "Kim", "Qee", "Part-time", 2021)
        review = create_review(staff.ID, student.ID, True, "This is a great review")
        oldReviewIsPositive = review.isPositive
        oldReviewComment = review.comment
        edit_review(review, staff, False, "This is a good review of a horrible student")
        assert admin and staff and student and review 
        assert review.isPositive != oldReviewIsPositive
        assert review.comment != oldReviewComment

    def test_delete_review(self): 
        admin = create_user("Green", "greenlast", "greenpass")
        staff = create_staff("Pem", "Ven", "password", "777", "pem@example.com", 2016)
        student = add_student_information(admin, "666", "Cem", "Sem", "Part-time", 2021)
        review = create_review(staff.ID, student.ID, True, "Soon to be deleted")
        assert admin and staff and student and review 
        delete_review(review, staff)
        assert get_review(review.ID) is None 

    def test_get_reviews_for_student(self): 
        admin = create_user("Red", "redlast", "redpass")
        staff = create_staff("Xem", "Zenm", "password", "111", "zenm@example.com", 2016)
        student = add_student_information(admin, "222", "Demn", "Sam", "Evening", 2022)
        assert admin and staff and student
        assert create_review(staff.ID, student.ID, True, "What a good student")
        assert create_review(staff.ID,  student.ID, True, "He answers all my questions in class")
        reviews = get_reviews_for_student(student.ID)
        for review in reviews: 
            assert review.studentID == student.ID 

    def test_get_reviews_by_staff(self): 
        admin = create_user("Blue", "bluelast", "bluepass")
        staff = create_staff("Forg", "Qu", "password", "3333", "qu@example.com", 2004)
        student = add_student_information(admin, "1111", "Ano", "One", "Full-Time", 2016)
        assert admin and staff and student
        assert create_review(staff.ID, student.ID, False, "What a bad student")
        assert create_review(staff.ID,  student.ID, False, "He always talk during class")
        reviews = get_reviews_by_staff(staff.ID)
        for review in reviews: 
            assert review.reviewerID == staff.ID 

    def test_upvote(self):
        admin = create_user("White", "whitelast", "whitepass")
        staff_1 = create_staff("Geo33", "Twin1", "password", "5555", "twin1@example.com", 2015)
        staff_2 = create_staff("Geo2", "Twin2", "password", "4444", "twin2@example.com", 2015)
        student = add_student_information(admin, "9999", "Kil", "Me", "Full-Time", 2020)
        review = create_review(staff_1.ID, student.ID, True, "Do i even need to review this student")
        assert admin and staff_1 and staff_2 and student and review
        old_upVotes = review.upvotes
        old_downvotes = review.downvotes
        assert old_upVotes + 1 == upvote(review.ID, staff_2) 
        assert old_downvotes == review.downvotes

    def test_downvote(self):
        admin = create_user("Black", "blacklast", "blackpass")
        staff_1 = create_staff("Geo", "Twin3", "password", "6666", "twin3@example.com", 2015)
        staff_2 = create_staff("Geo3", "Twin4", "password", "7777", "twin4@example.com", 2015)
        student = add_student_information(admin, "9998", "Still", "Here", "Full-Time", 2019)
        review = create_review(staff_1.ID, student.ID, False, "Do i even need to review this horrible thing called a student")
        assert admin and staff_1 and staff_2 and student and review
        old_upVotes = review.upvotes
        old_downvotes = review.downvotes
        assert old_upVotes == review.upvotes
        assert old_downvotes + 1 == downvote(review.ID, staff_2) 

    def test_get_rankings(self): 
        admin = create_user("Brown", "brownlast", "brownpass")
        assert admin
        for student in range (2011, 2021): 
            assert add_student_information(admin, str(student), "Fname" + str(student), "Lname" + str(student), "Full-Time", 2022)
        for staff in range (2000, 2010):
            assert create_staff(str(staff),"Fname" + str(staff), "Lname" + str(staff), "password2", str(staff) + "email@example.com", 2019)
            assert create_review(str(staff), str(staff + 11), random.choice([True, False]), "reviewing...") 
        for staff in range (2000, 2010):
            reviews = get_reviews_by_staff(str(staff))
            assert reviews 
            for review in reviews: 
                for voter in range (2000, 2010):
                    if get_staff(str(voter)).ID != review.reviewerID: 
                        assert random.choice([upvote(review.ID, get_staff(str(voter))), downvote(review.ID, get_staff(str(voter)))])
        assert get_student_rankings(get_staff(str(2000))) is not None
