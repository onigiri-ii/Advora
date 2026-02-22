from flask import Blueprint, request, jsonify, session
from services.supabase_service import supabase_service
from datetime import datetime

# Create the blueprint FIRST
entries_bp = Blueprint('entries', __name__)

if supabase_service:
    supabase = supabase_service.get_client()
else:
    supabase = None
    print("⚠️  Entries routes: Supabase not available")

@entries_bp.route('/api/entries', methods=['GET'])
def get_entries():
    """Get all entries for the logged-in user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if not supabase:
        return jsonify({'error': 'Database connection not available'}), 500
    
    try:
        # Get all journal entries with their symptoms and factors
        result = supabase.table('journal_entries') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('entry_date', desc=True) \
            .execute()
        
        # Manually fetch symptoms and factors for each entry
        entries_with_details = []
        for entry in result.data:
            # Get symptoms for this entry
            symptoms_result = supabase.table('entry_symptoms') \
                .select('symptoms(id, symptom_key, label, icon)') \
                .eq('entry_id', entry['id']) \
                .execute()
            
            # Get factors for this entry
            factors_result = supabase.table('entry_factors') \
                .select('*') \
                .eq('entry_id', entry['id']) \
                .execute()
            
            entry_with_details = {
                **entry,
                'symptoms': [s['symptoms'] for s in symptoms_result.data] if symptoms_result.data else [],
                'factors': factors_result.data[0] if factors_result.data else {}
            }
            entries_with_details.append(entry_with_details)
        
        return jsonify(entries_with_details), 200
    except Exception as e:
        print(f"Error fetching entries: {e}")
        return jsonify({'error': str(e)}), 500

@entries_bp.route('/api/entries', methods=['POST'])
def save_entry():
    """Save or update a journal entry"""
    user_id = session.get('user_id')
    print(f"Saving entry for user_id: {user_id}")
    
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if not supabase:
        return jsonify({'error': 'Database connection not available'}), 500
    
    data = request.json
    entry_date = data.get('entry_date')
    text = data.get('text', '')
    pain_level = data.get('pain_level', 3)
    symptoms = data.get('symptoms', [])
    factors = data.get('factors', {})
    
    try:
        # First, verify the user exists
        user_check = supabase.table('users') \
            .select('id') \
            .eq('id', user_id) \
            .execute()
        
        if not user_check.data:
            print(f"User {user_id} not found in database")
            return jsonify({'error': 'User not found'}), 401
        
        # Check if entry exists for this date
        existing = supabase.table('journal_entries') \
            .select('id') \
            .eq('user_id', user_id) \
            .eq('entry_date', entry_date) \
            .execute()
        
        print(f"Existing entry check: {existing.data}")
        
        if existing.data:
            # Update existing entry
            entry_id = existing.data[0]['id']
            print(f"Updating existing entry: {entry_id}")
            
            # Update journal entry
            update_result = supabase.table('journal_entries') \
                .update({
                    'text': text,
                    'pain_level': pain_level,
                    'updated_at': datetime.now().isoformat()
                }) \
                .eq('id', entry_id) \
                .eq('user_id', user_id) \
                .execute()
            
            print(f"Update result: {update_result}")
            
            # Delete existing symptoms and factors to replace them
            supabase.table('entry_symptoms').delete().eq('entry_id', entry_id).execute()
            supabase.table('entry_factors').delete().eq('entry_id', entry_id).execute()
        else:
            # Create new entry
            print(f"Creating new entry for user {user_id} on date {entry_date}")
            
            entry_result = supabase.table('journal_entries') \
                .insert({
                    'user_id': user_id,
                    'entry_date': entry_date,
                    'text': text,
                    'pain_level': pain_level
                }) \
                .execute()
            
            print(f"Insert result: {entry_result}")
            
            if not entry_result.data:
                return jsonify({'error': 'Failed to create entry'}), 500
                
            entry_id = entry_result.data[0]['id']
            print(f"Created entry with ID: {entry_id}")
        
        # Insert symptoms if any
        if symptoms and len(symptoms) > 0:
            print(f"Inserting symptoms: {symptoms}")
            
            # Get symptom IDs from keys
            symptom_ids = supabase.table('symptoms') \
                .select('id, symptom_key') \
                .in_('symptom_key', symptoms) \
                .execute()
            
            print(f"Found symptom IDs: {symptom_ids.data}")
            
            for symptom in symptom_ids.data:
                symptom_insert = supabase.table('entry_symptoms') \
                    .insert({
                        'entry_id': entry_id,
                        'symptom_id': symptom['id']
                    }) \
                    .execute()
                print(f"Inserted symptom: {symptom_insert}")
        
        # Insert factors
        factors_data = {
            'entry_id': entry_id,
            'period': factors.get('period', False),
            'period_flow': factors.get('period_flow') if factors.get('period') else None,
            'birth_control': factors.get('birth_control', False),
            'birth_control_type': factors.get('birth_control_type') if factors.get('birth_control') else None,
            'sick': factors.get('sick', False),
            'sick_type': factors.get('sick_type') if factors.get('sick') else None,
            'stress': factors.get('stress', 3)
        }
        
        print(f"Inserting factors: {factors_data}")
        
        factors_insert = supabase.table('entry_factors') \
            .insert(factors_data) \
            .execute()
        
        print(f"Factors insert result: {factors_insert}")
        
        return jsonify({'success': True, 'entry_id': entry_id}), 200
        
    except Exception as e:
        print(f"Error saving entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500