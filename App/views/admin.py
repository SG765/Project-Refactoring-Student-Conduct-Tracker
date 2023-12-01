from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from datetime import datetime, timedelta

from.index import index_views

from App.controllers import (
    create_user,
    jwt_authenticate,
    jwt_authenticate_admin,
)

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

@admin_views.route('/students', methods=['POST'])
def add_students():
  return jsonify({'message': f"Students added"})

@admin_views.route('/students', methods=['PUT'])
def update_students():
  return jsonify({'message': f"Students updated"})
