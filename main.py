import os
from flask import Flask, request, render_template, redirect, url_for, flash
import mindsdb_sdk
from datetime import datetime
import time
import json

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-fallback-key')

# Configuration
MINDSDB_SERVER = "http://127.0.0.1:47334"
KB_NAME = "herbal_remedy_kb"
OLLAMA_MODEL_NAME = "deepseek-r1:1.5b"  # Your Ollama model
OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama URL

def get_mindsdb_connection():
    return mindsdb_sdk.connect(MINDSDB_SERVER)

def init_ai_environment():
    try:
        conn = get_mindsdb_connection()
        
        # 1. Create Ollama ML Engine
        try:
            conn.query("DROP ML_ENGINE IF EXISTS ollama_engine")
        except Exception as e:
            print(f"Couldn't drop ollama_engine: {str(e)}")
            
        conn.query(f"""
        CREATE ML_ENGINE ollama_engine
        FROM ollama
        USING
            model_name = '{OLLAMA_MODEL_NAME}',
            base_url = '{OLLAMA_BASE_URL}'
        """)
        print("✅ Ollama ML Engine created")
        
        # 2. Create Knowledge Base with Ollama
        try:
            conn.query("DROP KNOWLEDGE BASE IF EXISTS herbal_remedy_kb")
        except Exception as e:
            print(f"Couldn't drop KB: {str(e)}")
            
        conn.query(f"""
        CREATE KNOWLEDGE BASE herbal_remedy_kb
        USING
            engine = 'ollama_engine',
            model_name = '{OLLAMA_MODEL_NAME}',
            input_columns = ['content'],
            metadata_columns = ['symptom', 'safety', 'source', 'timestamp']
        """)
        print("✅ Knowledge Base created with Ollama")
        
        # 3. Insert sample data
        sample_data = [
            ("Headache", "Safe for adults", "Ginger tea may help relieve headaches"),
            ("Cold", "Safe for all ages", "Tulsi leaves brewed in tea help with congestion")
        ]
        
        for symptom, safety, content in sample_data:
            conn.query(f"""
                INSERT INTO herbal_remedy_kb (symptom, safety, content)
                VALUES ('{symptom}', '{safety}', '{content.replace("'", "''")}')
            """)
        print("✅ Sample data inserted")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        return False
    

@app.route('/browse')
def browse():
    try:
        conn = get_mindsdb_connection()
        query_obj = conn.query(f"SELECT * FROM {KB_NAME} LIMIT 100")
        df = query_obj.fetch()

        results = []
        if df is not None and not df.empty:
            for row in df.to_dict('records'):
                try:
                    metadata = json.loads(row.get('metadata', '{}'))
                except json.JSONDecodeError:
                    metadata = {}

                results.append({
                    'symptom': metadata.get('symptom', 'General'),
                    'safety': metadata.get('safety', '-'),
                    'content': row.get('chunk_content', '-')
                })

            print("✅ Cleaned Records:", results)
        else:
            print("⚠️ No data returned.")
    except Exception as e:
        print(f"❌ Browse Error: {e}")
        results = []

    return render_template('browse.html', results=results)


# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    results = []

    if request.method == 'POST':
        query = request.form.get('query', '')
        symptom = request.form.get('symptom', '').strip()
        safety = request.form.get('safety', '').strip()

        try:
            conn = get_mindsdb_connection()
            safe_query = query.replace("'", "''")

            sql = f"""
                SELECT *
                FROM herbal_remedy_kb
                WHERE semantic_search('{safe_query}', herbal_remedy_kb.content)
            """

            if symptom and symptom != 'All':
                sql += f"\n  AND symptom = '{symptom}'"
                
            if safety and safety != 'All':
                if safety == 'safe':
                    sql += f"\n  AND safety LIKE '%Safe%'"
                elif safety == 'safe in small doses':
                    sql += f"\n  AND safety LIKE '%small doses%'"
                elif safety == 'avoid during pregnancy':
                    sql += f"\n  AND safety LIKE '%pregnancy%'"

            sql += "\nLIMIT 20;"

            print("📤 Executing SQL:", sql)
            df = conn.query(sql).fetch()
            print("📥 Results:", df.to_dict('records'))

            if df is not None and not df.empty:
                for r in df.to_dict('records'):
                    try:
                        metadata = json.loads(r.get('metadata', '{}'))
                        results.append({
                            'symptom': metadata.get('symptom', 'General'),
                            'safety': metadata.get('safety', '-'),
                            'content': r.get('chunk_content', r.get('content', '-'))
                        })
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            flash(f"Search error: {str(e)}", "error")

    return render_template('search.html', results=results)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Validate required fields first
        required_fields = ['content', 'symptom', 'safety']
        missing_fields = [field for field in required_fields if not request.form.get(field)]
        
        if missing_fields:
            flash(f'Missing required fields: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('add'))

        try:
            # Get and sanitize all inputs
            content = request.form['content'].replace("'", "''")
            symptom = request.form['symptom'].replace("'", "''")
            safety = request.form['safety'].replace("'", "''")
            source = request.form.get('source', 'user_submitted').replace("'", "''")
            
            try:
                efficacy = int(request.form.get('efficacy_rating', 3))
            except ValueError:
                efficacy = 3  # Default value if invalid number
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Get database connection
            conn = get_mindsdb_connection()
            if not conn:
                flash('Database connection failed', 'error')
                return redirect(url_for('add'))

            # Debug: Print the actual SQL query being executed
            sql_query = f"""
                INSERT INTO herbal_remedy_kb (content, symptom, safety, source, timestamp, efficacy_rating)
                VALUES (
                    '{content}',
                    '{symptom}',
                    '{safety}',
                    '{source}',
                    '{timestamp}',
                    {efficacy}
                )
            """
            print("Executing SQL:", sql_query)  # Debug log

            # Execute with error handling
            try:
                result = conn.query(sql_query)
                
                # Verify insertion
                if result and hasattr(result, 'affected_rows') and result.affected_rows > 0:
                    flash('Remedy added successfully!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Failed to add remedy - no rows affected', 'error')
            except Exception as e:
                error_msg = str(e)
                if "doesn't exist" in error_msg:
                    flash('Knowledge base not initialized. Please restart the application.', 'error')
                elif "duplicate key" in error_msg:
                    flash('This remedy already exists', 'error')
                else:
                    flash(f'Database error: {error_msg}', 'error')
                return redirect(url_for('add'))

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return redirect(url_for('add'))
    
    # GET request - show form
    return render_template('add.html')

    

if __name__ == '__main__':
    # Initialize with Ollama
    if init_ai_environment():
        print("✅ System initialized successfully with Ollama")
    else:
        print("❌ Failed to initialize with Ollama")
    
    app.run(debug=True, port=5001)

    