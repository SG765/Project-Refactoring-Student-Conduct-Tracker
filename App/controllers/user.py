from App.models import Staff, Student, Admin
from App.database import db


def create_staff(staffID, firstname, lastname, password, email, yearStartedTeaching):
    new_staff = Staff(staffID=staffID, firstname=firstname, lastname=lastname, password=password, email=email, yearStartedTeaching=yearStartedTeaching)
    if new_staff:
        db.session.add(new_staff)
        db.session.commit()
        return new_staff
    return None

def create_user(firstname, lastname, password):
    new_admin = Admin(firstname=firstname, lastname=lastname, password=password)
    if new_admin:
        db.session.add(new_admin)
        db.session.commit()
        return new_admin
    return None

def get_staff(staffID):
    return Staff.query.filter_by(ID=staffID).first()

def get_student(studentID):
    return Student.query.filter_by(ID=studentID).first()

def get_admin(adminID):
    return Admin.query.filter_by(ID=adminID).first()

def get_all_json(entities):
    if not entities:
        return []
    return [entity.to_json() for entity in entities]

def get_all_users_json():
    return get_all_json(get_all_users())

def get_all_students_json():
    return get_all_json(get_all_students())

def get_all_staff_json():
    return get_all_json(get_all_staff())

def get_entity(entity_class):
    return db.session.query(entity_class).all()

def get_all_users():
    return get_entity(Admin) + get_entity(Staff) + get_entity(Student)

def get_all_students():
    return get_entity(Student)

def get_all_staff():
    return get_entity(Staff)
    
