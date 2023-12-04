from App.controllers.user import get_student
from App.models import Admin
from App.database import db 

def add_student_information (admin, id, firstname, lastname, studentType, yearOfEnrollment):
    if get_student(id):
        return None
    return admin.addStudentInformation(id, firstname, lastname, studentType, yearOfEnrollment)

def update_student (admin, student, field_to_update, new_value):
    studentUpdated= admin.updateStudent(student, field_to_update, new_value)
    return studentUpdated
    