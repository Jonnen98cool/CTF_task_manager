from flask import request
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import send_from_directory
import random

from main import app
import backend.utils as utils
import backend.db_structure  as DB




@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method == "GET"):
        return send_from_directory("frontend/static/html", "login.html")

    elif(request.method == "POST"):
        res = make_response()
        value = request.form.get("credentials")   # This is the POST parameter the user sends
        if(value is None):
            res.data = "Error: expected parameter \"credentials\" was not received"
            res.status = 400

        else:
            user_row = DB.User.query.filter_by(session_id=value).first()   #Only one can exist (db settings)
            if(user_row is None):
                res.data = "Error: failed to authenticate, provided session id does not exist in database"
                res.status = 400    # Not 401 since /login does not require authentication
            else:
                res = make_response(redirect("/", code=302))
                res.set_cookie("auth", value=user_row.session_id, max_age=None, expires=None, path='/', secure=None, httponly=True, samesite="Lax")
                res.set_cookie("user", value=user_row.username, max_age=None, expires=None, path='/', secure=None, httponly=True, samesite="Lax")


        return res
        

    

@app.route("/", methods=["GET"])
def index():
    #if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    # Showing this static content is OK, even for unauthorized users
    return send_from_directory("frontend/static/html", "index.html")
    


# Get much of the database, e.g. all challenges
@app.route("/api", methods=["GET"])
def landing():
#     #Temp backdoor to change user on the fly
#     auth = request.args.get("auth")
#     if(auth is not None):
#         res = make_response()
#         res.status = 204
#         cookie_auth_value = "not_set"
#         cookie_user_value = "not_set"
#         if(auth == "3"):
#             cookie_user_value = "mrB4ckd00r"
#             cookie_auth_value = utils.generate_auth_cookie()
#             print(f"\033[94mAPP MESSAGE: Backdoor user created   {cookie_user_value} : {cookie_auth_value}\033[0m")
#             DB.db.session.add(DB.User(username=cookie_user_value, password="unimplemented", session_id=cookie_auth_value, role="participant"))
#             DB.db.session.commit()
# 
#         res.set_cookie("auth", value=cookie_auth_value, max_age=None, expires=None, path='/', secure=None, httponly=True, samesite="Lax")
#         res.set_cookie("user", value=cookie_user_value, max_age=None, expires=None, path='/', secure=None, httponly=True, samesite="Lax")
#         return res



    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401 

    # If user is authenticated but does not have cookie "user" set to the correct value, Fix that.
    cookie_auth_value = request.cookies.get("auth")
    user_row = DB.User.query.filter_by(session_id=cookie_auth_value).first()  # Since the user got past the 401 that means they are authenticated and have an account
    username = user_row.username
    cookie_user_value = request.cookies.get("user")
    set_cookie = True if cookie_user_value != username else False
 
    res = "empty"
    try:
        jsonified_db = utils.get_db_as_jsonified()  # Attempt to get db contents as a jsonified flask Response object
    except Exception as e:
        res = make_response("Error: failed to get contents from database")
        res.status = 500
    else:
        res = jsonified_db
        res.status = 200
        if(set_cookie == True): res.set_cookie("user", value=username, max_age=None, expires=None, path='/', secure=None, httponly=True, samesite="Lax")
        try:
            total_messages = DB.db.session.query(DB.Server).count()
            number = random.randint(2, total_messages)
            current = DB.Server.query.get(number).message
            res.headers["Server-Mood"] = current
        except:
            pass

    return res


    
@app.route("/api/add_challenge", methods=["POST"])
def add_challenge():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401

    res = make_response()
    #cname = request.form["cname"]      # Deprecated, will cause unhandled 500 if parameter doesnt exist
    cname = request.form.get("cname")   # This is the POST parameter the user sends
    if(cname is None):
        res.data = "Error: expected parameter \"cname\" was not received"
        res.status = 400

    else:  # Attempt to add user-requested challenge to db
        if(DB.db.session.query(DB.Challenge).filter_by(name=cname).first() is not None):
            res.data = "Error: challenge with that name already exists"
            res.status = 409
        else:
            try:
                new_challenge = DB.Challenge(name=cname)
                DB.db.session.add(new_challenge)
                DB.db.session.commit()
            except Exception as e:      
                #return jsonify({"Error": str(e)}), 400 #Warning, this gives verbose sql errors
                res.data = "Error: something went wrong when attempting to add challenge to database"     # This is not very verbose, for security reasons
                res.status = 500
            else:
                res.data = "Challenge created succesfully"
                res.status = 201

    return res


# Delete a challenge
@app.route("/api/delete_challenge/<int:c_id>", methods=["DELETE"])
def delete_challenge(c_id):
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401

    res = make_response()
    chall_to_del = DB.Challenge.query.get(c_id)
    
    if(chall_to_del is None):
        res.data = f"Error: could not perform deletion on challenge with id {str(c_id)}, it does not exist in the database"
        res.status = 404
    else:      
        challenge_markings = DB.ChallengeContents.query.filter_by(challenge_id=c_id).delete() #Delete challenge markings
        DB.db.session.delete(chall_to_del)  #Delete challenge
        try:
            DB.db.session.commit()
        except Exception as e:
            res.data = f"Error: could not delete challenge and/or challenge-associated markings from database"
            res.status = 500
        else:
            res.data = f"Succesfully deleted challenge with id {str(c_id)}"
            res.status = 200

    return res


# Update an existing challenge with a color that user marked it with
@app.route("/api/update_challenge", methods=["POST"]) 
def update_challenge():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
        
    res = make_response()
    try:    #Lots of things can go wrong
        content = request.json  
        
        user_cookie = request.cookies.get("auth")
        requested_by_user = DB.User.query.filter_by(session_id=user_cookie).first().username
        if(requested_by_user is None):  # This should never happen since 401 will return prior to this
            res.data = "Error: could not retrieve user associated with request cookie from database"
            res.status = 500

        else:
            rec_user = None if content["mark"] != 4 else content["recommendedUser"]
            new_update = DB.ChallengeContents(challenge_id=content["challengeId"], user=requested_by_user, mark=content["mark"], recommended_user=rec_user)
            existing_row = DB.ChallengeContents.query.filter_by(challenge_id=new_update.challenge_id, user=new_update.user).first()
            update_db = True

            # 6 means remove marking
            if(new_update.mark == 6):       
                if(existing_row is None):   # User attempts to delete a mark which they haven't made
                    res.data = "Error: can not remove non-existent marking"
                    res.status = 400
                    update_db = False
                else:
                    DB.db.session.delete(existing_row)
                    res.data = "Sucessfully removed marking"
                    res.status = 200 

            # User doesn't have an existing mark, create one       
            elif(existing_row is None):
                DB.db.session.add(new_update)          #Add new row
                res.data = "Succesfully added marking"
                res.status = 201
                
            #If user already made a mark on this challenge, update the mark
            else:
                # Selected mark was same as existing AND recommendedUser was the same too
                if(existing_row.mark == new_update.mark and existing_row.recommended_user == new_update.recommended_user):
                    res.data = "Mark was same as existing, database not updated"
                    res.status = 418
                    update_db = False
                else:
                    existing_row.mark = new_update.mark    #Update existing row
                    existing_row.recommended_user = new_update.recommended_user
                    res.data = "Succesfully updated marking"
                    res.status = 200


            if(update_db):   # Not all requests result in the db being updated
                try:   
                    DB.db.session.commit()
                except Exception as e:      
                    res.data = "Error: unhandled exception ocurred when attempting to update the database with received data"
                    res.status = 500

    except Exception as ex:
        res.data = "Error: unhandled exception occurred when processing your request"
        res.status = 500

    return res








#Admin stuff here
@app.route("/admin", methods=["GET"])
def admin():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    if(not utils.is_admin(request)): return "FORBIDDEN", 403

    return send_from_directory("frontend/static/html", "admin.html") 


@app.route("/admin/show_users", methods=["GET"])
def admin_show_users():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    if(not utils.is_admin(request)): return "FORBIDDEN", 403

    user_list = []
    users = DB.User.query.all()
    for user in users:
        #inner = {"id": user.id, "username": user.username, "role": user.role}
        inner = {"id": user.id, "username": user.username, "password": user.password, "session_id": user.session_id, "role": user.role}
        user_list.append(inner)

    retVal = jsonify({"Users": user_list})    
    return retVal
    
    

@app.route("/admin/add_user", methods=["POST"])
def admin_add_user():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    if(not utils.is_admin(request)): return "FORBIDDEN", 403

    user = request.form.get("username")
    user_cookie = utils.generate_auth_cookie()
    print(f"\033[94mAPP MESSAGE: /admin/add_user: Session id generated for user {user} is: {user_cookie}\033[0m")   # security=bad, adminuser-friendlyness=good
    DB.db.session.add(DB.User(username=user, password="unimplemented", session_id=user_cookie, role="participant"))
    try:
        DB.db.session.commit()
    except Exception as e:
        return jsonify({"Error": str(e)}), 500        # WARNING: verbose error
    else:
        return f"User added succesfully. Give them their session id to authenticate with: {user_cookie}", 201


# Could also implement that upon user deletion, delete all their markings. I don't think it's necessary though. You can just call /clear_challenges if it's that big of a problem.
@app.route("/admin/delete_user", methods=["POST"])
def admin_delete_user():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    if(not utils.is_admin(request)): return "FORBIDDEN", 403

    id_to_del = request.form.get("id")
    user_row = DB.User.query.get(id_to_del)
    if(user_row.role == "admin"):
        return "You can not delete an admin user (did you try to lock yourself out of the app? :O)", 400
    
    DB.db.session.delete(user_row)
    try:
        DB.db.session.commit()
    except Exception as e:
        return jsonify({"Error": str(e)}), 500        # WARNING: verbose error
    else:
        return f"User succesfully deleted", 200


@app.route("/admin/change_title", methods=["POST"])
def admin_change_title():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    if(not utils.is_admin(request)): return "FORBIDDEN", 403
    
    new_title = request.form.get("title")
    DB.Site.query.get(1).ctf_title = new_title  # It will always have id of 1
    try:
        DB.db.session.commit()
    except Exception as e:
        return jsonify({"Error": str(e)}), 500        # WARNING: verbose error
    else:
        return f"Title succesfully updated", 200


@app.route("/admin/clear_challenges", methods=["GET"])
def admin_clear_challenges():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    #if(not utils.is_admin(request)): return "FORBIDDEN", 403       # Not an admin-only operation

    DB.ChallengeContents.query.delete()
    DB.Challenge.query.delete()
    try:
        DB.db.session.commit()
    except Exception as e:
        return jsonify({"Error": str(e)}), 500        # WARNING: verbose error (+ anyone can do it)
    else:
        return f"Challenges succesfully deleted", 200


@app.route("/admin/clear_all", methods=["GET"])
def admin_clear_all():
    if(not utils.is_authenticated(request)): return "UNAUTHENTICATED", 401
    if(not utils.is_admin(request)): return "FORBIDDEN", 403

    DB.Site.query.get(1).ctf_title = "Lazy admin has neglected to update the title. Admin=bad"
    DB.User.query.filter(DB.User.role != "admin").delete()
    DB.ChallengeContents.query.delete()
    DB.Challenge.query.delete()
    try:
        DB.db.session.commit()
    except Exception as e:
        return jsonify({"Error": str(e)}), 500        # WARNING: verbose error
    else:
        return f"Challenges + non-admin users + ctf title succesfully deleted", 200






       
def main(admin_user:str, fresh_db:bool):
    if(fresh_db == True):
        utils.init_db(admin_user)
    else:
        with app.app_context():
            print(f"\033[94mAPP MESSAGE: Note: Existing database was chosen to be kept. Will NOT add new admin with username {admin_user}.\033[0m")
            admin_row = DB.User.query.filter_by(role="admin").first()
            print(f"\033[94mAPP MESSAGE: Existing admin is {admin_row.username} with session id: {admin_row.session_id}\033[0m")



    #NOTE: These are for debugging. Both should be commented out when running with a dedicated WSGI server.  
    #app.run(host="127.0.0.1", port=5000, debug=True)       # Localhost
    #app.run(host="0.0.0.0", port=5001, debug=False)        # Non-localhost
