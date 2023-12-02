from abc import ABC, abstractmethod
from App.database import db
from .student import Student
from sqlalchemy import ForeignKey


class Karma(db.Model):
  __tablename__ = "karma"
  karmaID = db.Column(db.Integer, primary_key=True)
  studentID = db.Column(db.String(10), db.ForeignKey('student.ID', use_alter=True))
  score = db.Column(db.Float, nullable=False, default=0.0)
  rank = db.Column(db.Integer, nullable=False, default=-99)

  def __init__(self, studentID, score=0.0, rank=-99):
    self.studentID= studentID
    self.score = score
    self.rank = rank

  def to_json(self):
    return {"karmaID": self.karmaID, 
            "studentID": self.studentID,
            "score": self.score, 
            "rank": self.rank}

# Calculate the karma score for the provided student based on reviews

  def calculate_total_score(self, student):
    karma_score = 0

    # Iterate through reviews associated with the student and calculate the karma
    for review in student.reviews:
      review.set_strategy()
      karma_strategy = review.karmaStrategy

      if karma_strategy:
        karma_score += karma_strategy.calculateScore(review)
  
    self.score= karma_score
    # connect the karma record to the student
    student.karmaID = self.karmaID

    db.session.add(self)
    db.session.commit()
    return self.score

  @classmethod
  def updateRank(cls):
    # Calculate the rank of students based on their karma score

    # Query all students with karma scores in descending order
    studentsOrdered = db.session.query(Student, Karma)\
               .join(Karma, Student.karmaID == Karma.karmaID)\
               .order_by(db.desc(Karma.score))\
               .all()

    rank = 1
    prev_score = None

    #assign ranks to student with the highest karma at the top
    for student, karma in studentsOrdered:
      if prev_score is None:
        prev_score = karma.score
        karma.rank = rank
      elif prev_score == karma.score:
        karma.rank = rank
      else:
        rank += 1
        karma.rank = rank
        prev_score = karma.score

      student.karmaID = karma.karmaID
  # Commit the changes to the database
    db.session.commit()

  @classmethod
  def getScore(cls, karmaID):
    # Retrieve the karma score by karma id
    karma = cls.query.filter_by(karmaID=karmaID).first()
    if karma:
      return karma.score
    return None

#strategy interface
class KarmaCalculationStrategy(ABC):
  @abstractmethod
  def calculateScore(self, review):
    pass

class CalculatePositiveKarmaStrategy(KarmaCalculationStrategy):
  def calculateScore(self, review):
    goodKarma = review.upvotes
    badKarma = review.downvotes
    return (goodKarma - badKarma)
  
class CalculateNegativeKarmaStrategy(KarmaCalculationStrategy):
  def calculateScore(self, review):
    goodKarma = review.downvotes
    badKarma = review.upvotes
    return (goodKarma - badKarma)