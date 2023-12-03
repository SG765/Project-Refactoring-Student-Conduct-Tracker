import random
from flask import Blueprint, render_template, jsonify
from App.controllers.admin import add_student_information
from App.controllers.review import downvote, upvote
from App.controllers.staff import create_review
from App.models import db
from App.controllers import create_user, create_staff
import randomname

from App.models.admin import Admin

index_views = Blueprint('index_views', __name__, template_folder='../templates')


# Define a route for the index view
@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

def generate_random_contact_number():
    return f"0000-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


@index_views.route('/init', methods=['POST'])
def init():
    db.drop_all()
    db.create_all()
    admin= create_user('bob', 'boblast' , 'bobpass')

    #create 48 staff members
    staff_list = []
    for ID in  range(2, 50): 
        staff= create_staff(
            str(ID), 
            randomname.get_name(), 
            randomname.get_name(), 
            randomname.get_name(), 
            randomname.get_name() + '@sta.uwi.edu', 
            random.randint(2008, 2022)
        )
        db.session.add(staff)
        staff_list.append(staff)
    db.session.commit()

    #create 100 students
    student_list = []
    for ID in range(50, 150): 
        student= add_student_information(admin, str(ID),
            randomname.get_name(), 
            randomname.get_name(), 
            random.choice(['Full-Time','Part-Time', 'Evening']),
            random.randint(2015, 2023)
        )
        db.session.add(student)
        student_list.append(student)
    db.session.commit()

    # Add 10 reviews by 10 random staff members for 10 random students
    review_list= []
    for staff in random.sample(staff_list, 10):
        student = random.choice(student_list)
        is_positive = random.choice([True, False])
        comment = f"This is a {'positive' if is_positive else 'negative'} review for {student.firstname} {student.lastname}."
        review = create_review(
            staffID=staff.ID,
            studentID=student.ID,
            is_positive=is_positive,
            comment=comment
        )
        db.session.add(review)
        review_list.append(review)
    db.session.commit()

    # Allow 30 random staff members to randomly upvote or downvote a review once
    for staff in random.sample(staff_list, 30):
        review= random.choice(review_list)
        # Check if the staff member is not the creator of the review
        if staff != review.reviewer:
            # Randomly upvote or downvote
            if random.choice([True, False]):
                upvote(reviewID=review.ID, staff=staff)
            else:
                downvote(reviewID=review.ID, staff=staff)
    db.session.commit()
    
    return jsonify({'message': 'Database initialized'}),201
