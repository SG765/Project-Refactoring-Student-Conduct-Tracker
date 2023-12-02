from App.controllers.user import get_staff, get_student
from App.models import Staff, Review

def create_review(staffID, studentID, is_positive, comment):
    staff = get_staff(str(staffID))
    student = get_student(str(studentID))
    review = staff.createReview(student, is_positive, comment)
    return review

def get_staff_reviews(staff_id):
    staff = get_staff(staff_id)
    return staff.getReviewsByStaff(staff)

def search_students_searchTerm(staff, searchTerm):
    return staff.searchStudent(searchTerm)
  
def get_student_rankings(staff):
    return staff.getStudentRankings()