from functools import wraps
from flask import render_template
from flask_login import current_user
from .models import Role, Permission
from . import db

def permission_required(permission):
    print("..")
    print(permission)
    """Restrict a view to users with the given permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return render_template("404.html", user=current_user)
            
            print(current_user)
            permissions = db.session.query(Permission.permission).join(Role.permission).filter(current_user.role_id == Permission.role_id,
                            Permission.permission == permission).first() 
            print(permission)   
            print(permissions)
            
            if permissions is not None:
                print("Permission granted.")
            else:
                print("Permission denied.")
            if permissions is None != permission:
                return render_template("404.html", user=current_user)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator