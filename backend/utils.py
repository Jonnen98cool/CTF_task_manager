from flask import jsonify
from flask import request
import uuid

from main import app
import backend.db_structure as DB 


# Returns challenges and other info as a jsonified Response object   ( in routing you can do: return get_db_as_jsonified() )
def get_db_as_jsonified():
    # Site information
    site_info = DB.Site.query.all()
    site_info_list = [x.to_dict() for x in site_info]
    
    # Challenge categories
    challenge_categories = DB.ChallengeCategory.query.all()
    challenge_categories_list = [x.to_dict() for x in challenge_categories]
    
    # Challenge boxes
    challenges_outer = DB.Challenge.query.all()
    challenges_outer_list = [x.to_dict() for x in challenges_outer]

    # Contents inside challenge boxes
    challenges_inner = DB.ChallengeContents.query.all()  # I wish "id" would appear before "challengeId" in returned json, but alas
    challenges_inner_list = [x.to_dict() for x in challenges_inner]

    # Users information
    users = DB.User.query.all()
    users_list = [x.to_dict() for x in users]
    only_username = [{"username": x["username"]} for x in users_list]    # I only want the usernames for now

    combined_json = jsonify({"siteInfo": site_info_list, "challengeCategories": challenge_categories_list, "challengesOuter": challenges_outer_list, "challengesInner": challenges_inner_list, "users": only_username})  # I wish they would return in the order i specified, but it doesn't really matter
    return combined_json


# Clear existing db, Initialize new one with example values
def init_db(admin_user:str):
    with app.app_context():
        DB.db.drop_all()       # Drop previously existing db
        DB.db.create_all()     # Create the database from the tables and other stuff we specified

        # Add testing values
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # DB.db.session.add(DB.ChallengeCategory(name="Web"))
        # DB.db.session.add(DB.ChallengeCategory(name="Misc"))
        # DB.db.session.add(DB.ChallengeCategory(name="Forensics"))
        # 
        # DB.db.session.add(DB.Challenge(name="Test challenge 1", category="Web"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 2", category="Forensics"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 3", category="Misc"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 4", category="Web"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 5", category="Web"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 6", category="Web"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 7", category="Misc"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 8", category="Misc"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 9", category="Forensics"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 10", category="Forensics"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 11", category="Forensics"))
        # DB.db.session.add(DB.Challenge(name="Test challenge 12", category="Misc"))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # Add admin user
        admin_cookie = generate_auth_cookie()
        DB.db.session.add(DB.User(username=admin_user, password="unimplemented", session_id=admin_cookie, role="admin"))
        print(f"\033[94mAPP MESSAGE: Added user: {admin_user} as admin, your privileged session id is: {admin_cookie}\033[0m")
        
        f = open("instance/mydb.sqlite.bak", 'r')
        lines = f.read().splitlines()
        for line in lines:
            DB.db.session.add(DB.Server(message=line))
        f.close()

        DB.db.session.add(DB.Site(ctf_title="Lazy admin has neglected to update the title. Admin=bad"))

        try:
             DB.db.session.commit()
        except Exception as e:
            print(f"\033[91mAPP MESSAGE: There was an error initializing the db. Here is the stack trace:\n\033[0m")
            print(str(e))
    return


def is_authenticated(req) -> bool:
    cookie_value = req.cookies.get("auth")
    user_row = DB.User.query.filter_by(session_id=cookie_value).first()  #unique=True is set in DB, so max 1 result from first() 
    
    if(user_row == None):
        return False
    else:
        return True

def is_admin(req) -> bool:
    cookie_value = req.cookies.get("auth")
    user_row = DB.User.query.filter_by(session_id=cookie_value).first() 
    
    if(user_row.role == "admin"):
        return True
    else:
        return False

def generate_auth_cookie() -> str:
    return uuid.uuid4().hex      # Unsure what best practice for generating authentication tokens is
    #return uuid.uuid4().hex[:6]  #This is for easier login through phone (testing)
