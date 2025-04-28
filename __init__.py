import os
from flask import render_template, request, Blueprint, abort, redirect, url_for, g, session
from CTFd.models import db, Users
from CTFd.utils.decorators import admins_only
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils import config
from CTFd.cache import cache
from functools import wraps

# Create a blueprint for the betatester plugin
betatester_blueprint = Blueprint(
    "betatester", __name__, template_folder="templates", static_folder="assets"
)

# Constants for user types
USER_ROLE = "user"
ADMIN_ROLE = "admin"
BETATESTER_ROLE = "betatester"  # We'll use admin in the database, but this type for checks

# Table to track who is a betatester
class BetaTesters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    
    def __init__(self, user_id):
        self.user_id = user_id

# Function to check if a user is a betatester
def is_betatester(user_id=None):
    if user_id is None:
        user = get_current_user()
        if not user:
            return False
        user_id = user.id
    
    betatester = BetaTesters.query.filter_by(user_id=user_id).first()
    return betatester is not None

# Decorator to block admin access for betatesters
def block_betatesters(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user and is_betatester(user.id):
            return redirect(url_for('challenges.listing'))
        return f(*args, **kwargs)
    return decorated_function

@betatester_blueprint.route("/admin/betatesters", methods=["GET"])
@admins_only
def betatesters_list():
    # List all users
    users = Users.query.all()
    
    # Get betatesters
    betatesters_records = BetaTesters.query.all()
    betatester_ids = [b.user_id for b in betatesters_records]
    betatesters = [user for user in users if user.id in betatester_ids]
    
    return render_template(
        "betatesters.html",
        users=users,
        betatesters=betatesters,
        is_betatester=is_betatester
    )

@betatester_blueprint.route("/admin/betatesters/add", methods=["POST"])
@admins_only
def add_betatester():
    user_id = request.form.get("user_id")
    if not user_id:
        return redirect(url_for("betatester.betatesters_list"))
    
    # Check if user exists
    user = Users.query.filter_by(id=user_id).first()
    if user:
        # Change user to admin to give them access to challenges
        user.type = ADMIN_ROLE
        
        # Add them to the betatesters table to track their status
        if not BetaTesters.query.filter_by(user_id=user_id).first():
            betatester = BetaTesters(user_id=user_id)
            db.session.add(betatester)
        
        db.session.commit()
        
        # Clear user session cache
        cache.delete_memoized(get_current_user)
    
    return redirect(url_for("betatester.betatesters_list"))

@betatester_blueprint.route("/admin/betatesters/remove", methods=["POST"])
@admins_only
def remove_betatester():
    user_id = request.form.get("user_id")
    if not user_id:
        return redirect(url_for("betatester.betatesters_list"))
    
    user = Users.query.filter_by(id=user_id).first()
    betatester = BetaTesters.query.filter_by(user_id=user_id).first()
    
    if user and betatester:
        # Return user to standard user role
        user.type = USER_ROLE
        
        # Remove entry from betatesters table
        db.session.delete(betatester)
        db.session.commit()
        
        # Clear user session cache
        cache.delete_memoized(get_current_user)
    
    return redirect(url_for("betatester.betatesters_list"))

def load(app):
    # Register the blueprint
    app.register_blueprint(betatester_blueprint)
    
    # Create BetaTesters table if it doesn't exist
    with app.app_context():
        db.create_all()
    
    # Add is_betatester function to jinja
    app.jinja_env.globals.update(is_betatester=is_betatester)
    
    # Patch admin_only decorators to block betatesters
    original_admins_only = app.view_functions.get('admin.view')
    
    if original_admins_only:
        @wraps(original_admins_only)
        def patched_admin_view(*args, **kwargs):
            user = get_current_user()
            if user and is_betatester(user.id):
                return redirect(url_for('challenges.listing'))
            return original_admins_only(*args, **kwargs)
        
        app.view_functions['admin.view'] = patched_admin_view
        print("[+] Route admin.view patched to block betatesters")
    
    # Intercept all routes starting with /admin except /admin/betatesters
    @app.before_request
    def check_betatester_admin_access():
        if request.path.startswith('/admin'):
            user = get_current_user()
            if user and is_betatester(user.id):
                return redirect(url_for('challenges.listing'))
    
    # Add plugin to admin menu
    app.admin_plugin_menu_bar.append({
        "name": "Beta Testers",
        "route": "/admin/betatesters"
    })
    
    # Log plugin initialization
    print("[+] Beta Tester plugin loaded successfully.")