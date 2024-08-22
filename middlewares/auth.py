from functools import wraps
from flask import jsonify, redirect, request
from flask_jwt_extended import (
    verify_jwt_in_request
)
from flask_socketio import disconnect
from services import user_service

def check_redirect(is_redirect: bool, msg: str):
    if is_redirect:
        return redirect('login', code=302)
    else: 
        return {"status_code": 401, "error": msg}, 401  

def jwt_required(is_redirect = True):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                claims = verify_jwt_in_request(optional=True)
                if claims is None:
                    return check_redirect(is_redirect, "token not valid")    

                user_id = int(claims[1]["sub"])
                user = user_service.get_by_id(user_id)  
                if user is None:
                    return check_redirect(is_redirect, "user does not exist")    

                request.user_id = int(claims[1]["sub"])
                request.role = user.role
                return fn(*args, **kwargs)
            except Exception as e:
                print(e)
                return check_redirect(is_redirect, str(e))  
            
        return decorator

    return wrapper

def jwt_ws_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                claims = verify_jwt_in_request(optional=True)
                if claims is None:
                    return disconnect()

                user_id = int(claims[1]["sub"])
                user = user_service.get_by_id(user_id)  
                if user is None:
                    return disconnect()

                request.user_id = int(claims[1]["sub"])
                request.role = user.role
                return fn(*args, **kwargs)
            except Exception as e:
                print(e)
                return disconnect()
            
        return decorator

    return wrapper

def admin_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                if request.user_id is None:
                    return {"status_code": 403, "error": "You are not authorized"}, 403

                if request.role in roles:
                    return fn(*args, **kwargs)
                else:
                    return {"status_code": 403, "error": "You are not authorized"}, 403

            except Exception as e:
                print(e)
                return jsonify({"status_code": 403, "error": "You are not authorized"}), 403
            
        return decorator

    return wrapper