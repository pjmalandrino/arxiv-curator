"""Authentication routes."""

from flask import Blueprint, jsonify, current_app
from ..auth import require_auth, require_admin, get_current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/me')
@require_auth
def get_user_info():
    """Get current user information."""
    user = get_current_user()
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'roles': user.roles,
        'is_admin': user.is_admin()
    })


@auth_bp.route('/admin/test')
@require_admin  
def admin_test():
    """Test admin-only endpoint."""
    user = get_current_user()
    return jsonify({
        'message': 'Admin access confirmed',
        'user': user.username
    })


@auth_bp.route('/user/profile')
@require_auth
def get_user_profile():
    """Get extended user profile."""
    user = get_current_user()
    return jsonify({
        'profile': {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'roles': user.roles,
            'permissions': user.permissions,
            'is_admin': user.is_admin()
        },
        'preferences': {
            # Placeholder for user preferences
            'theme': 'light',
            'notifications': True
        }
    })
