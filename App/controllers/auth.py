from functools import wraps
from flask_login import current_user, LoginManager, login_user
from App.database import db
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

from App.models import Staff, Admin, User

jwt = JWTManager()

def jwt_authenticate(id, password, model):
    user = model.query.filter_by(ID=id).first()
    if user and user.check_password(password):
        return create_access_token(identity=id)
    return None

def jwt_authenticate_staff(id, password):
    return jwt_authenticate(id, password, Staff)

def jwt_authenticate_admin(id, password):
    return jwt_authenticate(id, password, Admin)

def get_user(id, model):
    return model.query.filter_by(ID=id).first()

def login(id, password):    
    for model in [Staff, Admin]:
        user = get_user(id, model)
        if user and user.check_password(password):
            return user
    return None

def setup_flask_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        for model in [Staff, Admin]:
            user = get_user(user_id, model)
            if user:
                return user
        return login_manager

def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        admin = Admin.query.filter_by(ID=identity).one_or_none()
        if admin:
            return admin.ID

        staff = Staff.query.filter_by(ID=identity).one_or_none()
        if staff:
            return staff.ID
        
        return None


    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]

        admin = Admin.query.filter_by(ID=identity).one_or_none()
        if admin:
            return admin

        staff = Staff.query.filter_by(ID=identity).one_or_none()
        if staff:
            return staff

        return jwt

def staff_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Staff):
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper 