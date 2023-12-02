from datetime import datetime
from App.database import db

class Student(db.Model):
	__tablename__ = 'student'
	ID = db.Column(db.String(10), primary_key= True)
	firstname = db.Column(db.String(120), nullable= False)
	lastname = db.Column(db.String(120), nullable= False)
	studentType = db.Column(db.String(30))  #full-time, part-time or evening
	yearOfEnrollment = db.Column(db.Integer, nullable=False)
	yearOfStudy = db.Column(db.Integer)
	reviews = db.relationship('Review', backref='student', lazy='joined')
	karmaID = db.Column(db.Integer, db.ForeignKey('karma.karmaID', name='fk_karma_student', use_alter=True))

  #When student is newly created there would be no reviews or karma yet
	def __init__(self, studentID, firstname, lastname, studentType, yearofEnrollment):
		self.ID = studentID
		self.firstname = firstname
		self.lastname = lastname
		self.studentType = studentType
		self.yearOfEnrollment = yearofEnrollment
		self.yearOfStudy = self.calculate_year_study()
		self.reviews = []
	
	def get_id(self):
		return self.ID

#Gets the student details and returns in JSON format
	def to_json(self):
		karma = self.getKarma()
		return {
        "studentID": self.ID,
        "firstname": self.firstname,
        "lastname": self.lastname,
        "studentType": self.studentType,
		"yearOfEnrollment": self.yearOfEnrollment,
        "yearOfStudy": self.yearOfStudy, 
        "reviews": [review.to_json() for review in self.reviews],
		"karmaScore": karma.score if karma else None,
        "karmaRank": karma.rank if karma else None,
    }

	def calculate_year_study(self,current_date=None):#Dynamically calculate year based on enrollment date
		if current_date is None:
			current_date = datetime.now() 
		
		year_of_study = current_date.year - self.yearOfEnrollment
		
		# Adjust the year of study based on the current date
		if current_date.month >= 9:  # If it's September or later since academic year begins in september
			year_of_study += 1
			
		return max(1, year_of_study)

#get karma record from the karma table using the karmaID attached to the student
	def getKarma(self):
		from .karma import Karma
		return Karma.query.filter_by(studentID=self.ID).first()
