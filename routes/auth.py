from flask import Blueprint, request, jsonify, session
from services.supabase_client import SupabaseService

auth_bp = Blueprint('auth', __name__)
supabase = SupabaseService()

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        # Use Supabase Auth
        response = supabase.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        session['user_id'] = response.user.id
        session['access_token'] = response.session.access_token
        
        return jsonify({
            'success': True,
            'user': {
                'id': response.user.id,
                'email': response.user.email
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register new user"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    age = data.get('age')
    
    try:
        # Create auth user
        response = supabase.supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        # Create profile
        profile_data = {
            'id': response.user.id,
            'full_name': name,
            'age': age
        }
        supabase.create_user_profile(profile_data)
        
        session['user_id'] = response.user.id
        session['access_token'] = response.session.access_token
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    profile = supabase.get_user_profile(user_id)
    return jsonify(profile)