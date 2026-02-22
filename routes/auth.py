from flask import Blueprint, request, jsonify, session
from services.supabase_service import supabase_service

# Create blueprint FIRST
auth_bp = Blueprint('auth', __name__)

if supabase_service:
    supabase = supabase_service.get_client()
else:
    supabase = None
    print("⚠️  Auth routes: Supabase not available")

@auth_bp.route('/api/login', methods=['POST'])
def login():
    print("\n" + "="*50)
    print("LOGIN ATTEMPT DETECTED")
    print("="*50)
    
    if not supabase:
        print("❌ Supabase not available")
        return jsonify({'error': 'Database connection not available'}), 500
    
    # Get request data
    data = request.json
    print(f"📨 Request data received: {data}")
    
    email = data.get('email')
    password = data.get('password')
    
    print(f"📧 Email: '{email}'")
    print(f"🔑 Password: '{password}'")
    
    try:
        # Query user from Supabase
        print("\n🔍 Querying Supabase for user...")
        result = supabase.table('users') \
            .select('*') \
            .eq('email', email) \
            .execute()
        
        print(f"📊 Query result: {result.data}")
        
        if not result.data:
            print("❌ No user found with that email")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = result.data[0]
        print(f"✅ Found user: {user['email']}")
        print(f"🔐 Stored password: '{user['password']}'")
        print(f"🔐 Provided password: '{password}'")
        
        # Check password
        if user['password'] == password:
            print("✅ Password match!")
            
            # Set session
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session.permanent = True
            
            print(f"✅ Session set - user_id: {session.get('user_id')}")
            print(f"✅ Session set - user_email: {session.get('user_email')}")
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'age': user['age']
                }
            }), 200
        else:
            print("❌ Password mismatch!")
            print(f"   Expected: '{user['password']}'")
            print(f"   Got: '{password}'")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    print("✅ User logged out, session cleared")
    return jsonify({'success': True}), 200

@auth_bp.route('/api/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    print(f"Getting current user - session user_id: {user_id}")
    
    if not user_id:
        return jsonify({'user': None}), 200
    
    if not supabase:
        return jsonify({'error': 'Database connection not available'}), 500
    
    try:
        result = supabase.table('users') \
            .select('id, email, name, age') \
            .eq('id', user_id) \
            .execute()
        
        if result.data:
            print(f"✅ Found user in database: {result.data[0]['email']}")
            return jsonify({'user': result.data[0]}), 200
        else:
            print("❌ User not found in database, clearing session")
            session.clear()
            return jsonify({'user': None}), 200
    except Exception as e:
        print(f"Error fetching user: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/debug/users', methods=['GET'])
def debug_users():
    """Debug endpoint to check users in database"""
    if not supabase:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        result = supabase.table('users').select('id, email, name, age').execute()
        return jsonify({
            'users': result.data,
            'count': len(result.data)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        'session_exists': bool(session),
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'user_email': session.get('user_email')
    }), 200

@auth_bp.route('/api/setup/test-users', methods=['GET'])
def setup_test_users():
    """Temporary endpoint to insert test users"""
    if not supabase:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        # Check if users already exist
        existing = supabase.table('users').select('email').execute()
        existing_emails = [u['email'] for u in existing.data]
        
        results = []
        
        if 'sarah@test.com' not in existing_emails:
            result1 = supabase.table('users').insert({
                'email': 'sarah@test.com',
                'password': 'test123',
                'name': 'Sarah',
                'age': 28
            }).execute()
            results.append('sarah@test.com inserted')
        
        if 'demo@advora.com' not in existing_emails:
            result2 = supabase.table('users').insert({
                'email': 'demo@advora.com',
                'password': 'demo123',
                'name': 'Demo User',
                'age': 32
            }).execute()
            results.append('demo@advora.com inserted')
        
        if not results:
            results.append('Test users already exist')
        
        # Get updated list
        updated = supabase.table('users').select('email, password, name').execute()
        
        return jsonify({
            'message': 'Setup complete',
            'results': results,
            'users_in_db': updated.data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500