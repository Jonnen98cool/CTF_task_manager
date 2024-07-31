from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from main import app

 

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite"  # Name of db file to use. sqlite works well with Flask.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable query logging

db = SQLAlchemy(app) # This is our python db object. We use this to modify our actual database file.



# Define tables and their columns

class Challenge(db.Model):  
    __tablename__ = "challenge"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)

    def to_dict(self):
        return {
        "id": self.id,
        "name": self.name
        }

class ChallengeContents(db.Model):
    __tablename__ = "challenge_contents"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('challenge.id'))
    user: Mapped[str] = mapped_column(db.String, unique=False, nullable=False)
    mark: Mapped[int] = mapped_column(db.Integer, unique=False, nullable=False)
    recommended_user: Mapped[str] = mapped_column(db.String, unique=False, nullable=True)  # Could instead store user primary key
    
    def to_dict(self):
        return {
        "id": self.id,
        "challengeId": self.challenge_id,
        "user": self.user,
        "mark": self.mark,
        "recommended_user": self.recommended_user
         }


class User(db.Model):
    __tablename__ = "user"
    #The concepts cookie, session/sessionId and token are all similar. So what's the difference?
    #Cookie: a value stored in your browser. Can be eg. a session which contains a 32 char long string.
    #Session id: after authentication (login), that user is given a session id which identifies and authenticates them. They now use the session id (in a cookie) for authentication instead of having to login again for every action. This is typically a hard-to-guess randomized string.
    #Token: (conflicting opinions on this one) typically a value used for communication between multiple independent parties granting limited access to their data. A token typically contains usable data as opposed to randomized.
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String, unique=False, nullable=False)   #TODO: passwords should be hashed+salted
    session_id: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)  #TODO: shouldn't this also be hashed?
    role: Mapped[str] = mapped_column(db.String, unique=False, nullable=False)

    def to_dict(self):
        return {
        "id": self.id,
        "username": self.username,
        "password": self.password,
        "session_id": self.session_id,        # Wait a minute, should this be camelCase since it's converted to json?
        "role": self.role
        }


class Server(db.Model):
    __tablename__ = "server"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    message: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)


class Site(db.Model):  
    __tablename__ = "site"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)       # Not really necessary, but possibly good practice
    ctf_title: Mapped[str] = mapped_column(db.String, unique=False, nullable=False)

    def to_dict(self):
        return {
        "id": self.id,
        "ctf_title": self.ctf_title
        }
