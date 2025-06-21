from flask import Flask, request, render_template, redirect, url_for, flash
from mindsdb_sdk import connect

from datetime import datetime, timedelta
import json
from json import dumps
from dotenv import load_dotenv
import os
from src.core.queries import embedding_model, PROMPT_TEMPLATE, CREATE_AGENT_QUERY, SELECT_ANSWER_QUERY
import nest_asyncio
import requests

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-fallback-key')

# Configuration
MINDSDB_SERVER = os.getenv("MINDSDB_SERVER", "http://127.0.0.1:47334")
PROJECT_NAME = "herbal_rem"
KB_NAME = f"{PROJECT_NAME}.remedy_kb"

# Initialize MindsDB connection
server = connect(MINDSDB_SERVER)
files_db = server.get_database("files")

MINDSDB_API_URL = "http://localhost:47334/api"  # Adjust if your MindsDB runs elsewhere

def run_query(query: str):
    try:
        return server.query(query).fetch()
    except Exception as e:
        print(f"Query error: {str(e)}")
        return None

def init_ai_environment():
    try:
        # Create project if it doesn't exist
        try:
            server.create_project(PROJECT_NAME)
            print(f"Created project: {PROJECT_NAME}")
        except Exception as e:
            print(f"Project {PROJECT_NAME} might already exist: {str(e)}")
        
        # Create Knowledge Base
        create_kb_query = """
        CREATE KNOWLEDGE BASE IF NOT EXISTS herbal_rem.remedy_kb
        USING
            embedding_model = {embedding_model},
            content_columns = ['content'],
            metadata_columns = ['symptom', 'safety', 'source', 'timestamp'],
            id_column = 'id';
        """.format(embedding_model=dumps(embedding_model))
        try:
            run_query(create_kb_query)
            print(f"Created knowledge base: {KB_NAME}")
        except Exception as e:
            print(f"Knowledge base {KB_NAME} might already exist: {str(e)}")
        
        # Insert data from temporary table into knowledge base
        try:
            insert_kb_query = """
            INSERT INTO herbal_rem.remedy_kb (
                SELECT 
                    id,
                    symptom,
                    safety,
                    content,
                    source,
                    timestamp
                FROM files.herbal_data
            );
            """
            run_query(insert_kb_query)
            print("Inserted data into knowledge base")
        except Exception as e:
            print(f"Error inserting data into knowledge base: {str(e)}")
        
        # Create Agent
        try:
            run_query(CREATE_AGENT_QUERY)
            print(f"Created agent: {PROJECT_NAME}.remedy_agent")
        except Exception as e:
            print(f"Agent {PROJECT_NAME}.remedy_agent might already exist: {str(e)}")
        
        # Create index on the knowledge base for faster search
        try:
            create_index_query = "CREATE INDEX ON KNOWLEDGE_BASE herbal_rem.remedy_kb;"
            run_query(create_index_query)
            print("Created index on knowledge base herbal_rem.remedy_kb")
        except Exception as e:
            print(f"Error creating index: {str(e)}")

        return True
        
    except Exception as e:
        # print(f"Initialization failed: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []

    if request.method == 'POST':
        query = request.form.get('query', '')
        symptom = request.form.get('symptom', '').strip()
        safety = request.form.get('safety', '').strip()

        try:
            safe_query = query.replace("'", "''")

            sql = f"""
                SELECT *
                FROM {KB_NAME}
                WHERE semantic_search('{safe_query}', remedy_kb.content)
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

            # print("\U0001F4E4 Executing SQL:", sql)
            df = run_query(sql)
            # print("\U0001F4E5 Results:", df.to_dict('records') if df is not None else "None")

            if df is not None and not df.empty:
                for r in df.to_dict('records'):
                    try:
                        # Parse the metadata JSON string
                        metadata = json.loads(r.get('metadata', '{}'))
                        results.append({
                            'symptom': metadata.get('symptom', 'General'),
                            'safety': metadata.get('safety', '-'),
                            'content': r.get('chunk_content', r.get('content', '-')),
                            'source': metadata.get('source', '-')
                        })
                    except json.JSONDecodeError:
                        # Fallback if metadata parsing fails
                        results.append({
                            'symptom': 'General',
                            'safety': '-',
                            'content': r.get('chunk_content', r.get('content', '-'))
                        })

        except Exception as e:
            flash(f"Search error: {str(e)}", "error")

    return render_template('search.html', results=results)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        required_fields = ['content', 'symptom', 'safety']
        missing_fields = [field for field in required_fields if not request.form.get(field)]
        
        if missing_fields:
            flash(f'Missing required fields: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('add'))

        try:
            content = request.form['content'].replace("'", "''")
            symptom = request.form['symptom'].replace("'", "''")
            safety = request.form['safety'].replace("'", "''")
            source = request.form.get('source', 'user_submitted').replace("'", "''")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert into temporary table
            insert_query = f"""
    INSERT INTO herbal_rem.remedy_kb (content, symptom, safety, source, timestamp)
    VALUES (
        '{content}',
        '{symptom}',
        '{safety}',
        '{source}',
        '{timestamp}'
    )
""" 
            run_query(insert_query)
            
            # Insert into knowledge base
            kb_insert_query = f"""
                INSERT INTO {KB_NAME}
                SELECT id, symptom, safety, content, source, timestamp
                FROM files.herbal_temp
                WHERE id = LAST_INSERT_ID();
            """
            run_query(kb_insert_query)
            
            flash('Remedy added successfully!', 'success')
            return redirect(url_for('search'))

        except Exception as e:
            flash(f'Error adding remedy: {str(e)}', 'error')
            return redirect(url_for('add'))
    
    return render_template('add.html')

@app.route('/browse')
def browse():
    results = []
    try:
        sql = f"""
            SELECT *
            FROM {KB_NAME}
            LIMIT 100;
        """
        df = run_query(sql)
        if df is not None and not df.empty:
            for r in df.to_dict('records'):
                try:
                    # Parse the metadata JSON string
                    metadata = json.loads(r.get('metadata', '{}'))
                    results.append({
                        'symptom': metadata.get('symptom', 'General'),
                        'safety': metadata.get('safety', '-'),
                        'content': r.get('chunk_content', r.get('content', '-')),
                        'source': metadata.get('source', '-'),
                        'timestamp': metadata.get('timestamp', '-')
                    })
                except json.JSONDecodeError:
                    # Fallback if metadata parsing fails
                    results.append({
                        'symptom': 'General',
                        'safety': '-',
                        'content': r.get('chunk_content', r.get('content', '-')),
                        'source': '-',
                        'timestamp': '-'
                    })
    except Exception as e:
        flash(f"Browse error: {str(e)}", "error")
    return render_template('browse.html', results=results)

@app.route('/agent_status', methods=['GET', 'POST'])
def agent_status():
    answer = None
    question = ''
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            try:
                sql = SELECT_ANSWER_QUERY.format(question=question.replace("'", "''"))
                df = run_query(sql)
                if df is not None and not df.empty and 'answer' in df:
                    answer = df['answer'][0]
            except Exception as e:
                answer = f"Error: {str(e)}"
    return render_template('agent_status.html', answer=answer, question=question)

def agent_exists():
    try:
        # Try a harmless query to the agent
        test_query = """
            SELECT answer
            FROM herbal_rem.remedy_agent
            WHERE question = 'ping';
        """
        result = run_query(test_query)
        # If no error, agent exists
        return True
    except Exception as e:
        # print(f"Agent check error: {e}")
        return False

def create_mindsdb_job(project_name, payload):
    url = f"{MINDSDB_API_URL}/projects/{project_name}/jobs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        return response.status_code, response.json()
    except Exception:
        return response.status_code, response.text

@app.route('/create_job', methods=['GET', 'POST'])
def create_job():
    if request.method == 'POST':
        job_name = request.form['name']
        schedule_str = request.form.get('schedule_str', '').strip()
        query = request.form['query']

        # Get current time and add 1 year for end_at
        now = datetime.now()
        start_at = now.strftime('%Y-%m-%d %H:%M:%S')
        end_at = (now + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')

        job_payload = {
            "job": {
                "name": job_name,
                "query": query,
                "start_at": start_at,
                "end_at": end_at  # Added required end_at parameter
            }
        }

        if schedule_str:
            job_payload["job"]["schedule_str"] = schedule_str

        try:
            status_code, response_json = create_mindsdb_job(PROJECT_NAME, job_payload)
            if status_code in (200, 201):
                flash('Job created successfully!', 'success')
            else:
                flash(f'Failed to create job: {response_json}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('create_job'))

    return render_template('create_job.html')

if __name__ == '__main__':
    if init_ai_environment():
        print("✅ System initialized successfully")
    app.run(debug=True, port=5001) 