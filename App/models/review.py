from App.database import db
from .student import Student
from .karma import Karma
from datetime import datetime
from .karma import *

# Define the association table for staff upvotes on reviews
review_staff_upvoters = db.Table(
    'review_staff_upvoters',
    db.Column('reviewID', db.Integer, db.ForeignKey('review.ID')),
    db.Column('staffID', db.String(10), db.ForeignKey('staff.ID')),
)

review_staff_downvoters = db.Table(
    'review_staff_downvoters',
    db.Column('reviewID', db.Integer, db.ForeignKey('review.ID')),
    db.Column('staffID', db.String(10), db.ForeignKey('staff.ID')),
)

class Review(db.Model):
  __tablename__ = 'review'
  ID = db.Column(db.Integer, primary_key=True)
  reviewerID = db.Column(
      db.String(10),
      db.ForeignKey('staff.ID'))  #each review has 1 creator

  #create reverse relationship from Staff back to Review to access reviews created by a specific staff member
  reviewer = db.relationship('Staff',
                             backref=db.backref('reviews_created',
                                                lazy='joined'),
                             foreign_keys=[reviewerID])

  studentID = db.Column(db.String(10), db.ForeignKey('student.ID'))

  staffUpvoters = db.relationship(
      'Staff',
      secondary=review_staff_upvoters,
      backref=db.backref(
          'reviews_upvoted',
          lazy='joined'))  #for staff who have voted on the review

  staffDownvoters = db.relationship(
      'Staff',
      secondary=review_staff_downvoters,
      backref=db.backref(
          'reviews_downvoted',
          lazy='joined'))  #for staff who have voted on the review

  upvotes = db.Column(db.Integer, nullable=False)
  downvotes = db.Column(db.Integer, nullable=False)
  isPositive = db.Column(db.Boolean, nullable=False)
  created = db.Column(db.DateTime, default= (datetime.utcnow()))
  comment = db.Column(db.String(400), nullable=False)
  karmaStrategy = None

  # initialize the review. when it is created the date is automatically gotten and votes are at 0
  def __init__(self, reviewer, student, isPositive, comment):
    self.reviewerID = reviewer.ID
    self.reviewer = reviewer
    self.studentID = student.ID
    self.isPositive = isPositive
    self.comment = comment
    self.upvotes = 0
    self.downvotes = 0
    self.created = datetime.now()
    self.karmaStrategy= CalculatePositiveKarmaStrategy() if self.isPositive else CalculateNegativeKarmaStrategy()

  def get_id(self):
    return self.ID
  
  def set_strategy(self):
    if self.isPositive == True:
      self.karmaStrategy = CalculatePositiveKarmaStrategy()

    if self.isPositive == False:
      self.karmaStrategy = CalculateNegativeKarmaStrategy()

#allows the comment and whether the review is positive to be edited if the staff member is the creator of the review, returns none if not

  def editReview(self, staff, isPositive, comment):
    if self.reviewer == staff:
      self.isPositive = isPositive
      self.comment = comment
      db.session.add(self)
      db.session.commit()
      return True
    return None

  #deletes the review when called if the staff memeber is the creator of the review, return none if not

  def deleteReview(self, staff):
    if self.reviewer == staff:
      db.session.delete(self)
      db.session.commit()
      return True
    return None

  #adds 1 to the upvotes for the review when called
  def upvoteReview(self, staff): 
    self.karmaStrategy= self.set_strategy()
    db.session.add(self)
    db.session.commit()

    if staff in self.staffUpvoters:  # If they upvoted the review already, return current votes
      return self.upvotes
    else:
      if staff not in self.staffUpvoters:  #if staff has not upvoted allow the vote
        self.upvotes += 1
        self.staffUpvoters.append(staff)

        if staff in self.staffDownvoters:  #if they had downvoted previously then remove their downvote to account for switching between votes
          self.downvotes -= 1
          self.staffDownvoters.remove(staff)

    db.session.add(self)
    db.session.commit()

    # Retrieve the associated Student object using studentID
    student = Student.query.get(self.studentID)
    student_karma = Karma.query.filter_by(studentID= self.studentID).first()

    # Check if the student has a Karma record and create a new Karma record for them if not
    if student_karma is None:
      student_karma = Karma(self.studentID, score=0.0, rank=-99)
      db.session.add(student_karma)  # Add the Karma record to the session
      db.session.flush()
      db.session.commit()

    # Update Karma for the student
    if student_karma is not None:
      student_karma.calculate_total_score(student)
      student_karma.updateRank()
      db.session.add(student)
      db.session.add(student_karma)
      db.session.commit()

    return self.upvotes


  #adds 1 to the downvotes for the review when called
  def downvoteReview(self, staff): 
    self.karmaStrategy= self.set_strategy()
    db.session.add(self)
    db.session.commit()

    if staff in self.staffDownvoters:  # If they downvoted the review already, return current votes
      return self.downvotes

    else:
      if staff not in self.staffDownvoters:  #if staff has not downvoted allow the vote
        self.downvotes += 1
        self.staffDownvoters.append(staff)

        if staff in self.staffUpvoters:  #if they had upvoted previously then remove their upvote to account for switching between votes
          self.upvotes -= 1
          self.staffUpvoters.remove(staff)

      db.session.add(self)
      db.session.commit()
      
     # Retrieve the associated Student object using studentID
    student = Student.query.get(self.studentID)
    student_karma = Karma.query.filter_by(studentID= self.studentID).first()

    # Check if the student has a Karma record and create a new Karma record for them if not
    if student_karma is None:
      student_karma = Karma(self.studentID, score=0.0, rank=-99)
      db.session.add(student_karma)  # Add the Karma record to the session
      db.session.flush()
      db.session.commit()

    # Update Karma for the student
    if student_karma is not None:
      student_karma.calculate_total_score(student)
      student_karma.updateRank()
      db.session.add(student)
      db.session.add(student_karma)
      db.session.commit()

    return self.downvotes

  #return json representation of the review

  def to_json(self):
    return {
        "reviewID": self.ID,
        "reviewer": self.reviewer.firstname + " " + self.reviewer.lastname,
        "studentID": self.student.ID,
        "studentName": self.student.firstname + " " + self.student.lastname,
        "created":
        self.created.strftime("%d-%m-%Y %H:%M"),  #format the date/time
        "isPositive": self.isPositive,
        "upvotes": self.upvotes,
        "downvotes": self.downvotes,
        "comment": self.comment
    }
