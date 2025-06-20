from json import dumps
from os import getenv

embedding_model = {
    "provider": "ollama",
    "model_name": "deepseek-r1:1.5b",
    "base_url": "http://host.docker.internal:11434"
}

CREATE_KNOWLEDGE_BASE_QUERY = """
CREATE KNOWLEDGE BASE IF NOT EXISTS herbal_rem.remedy_kb
USING
    embedding_model = {embedding_model},
    content_columns = ['content'],
    metadata_columns = ['symptom', 'safety', 'source', 'timestamp'],
    id_column = 'id';
""".format(
    embedding_model=dumps(embedding_model)
)

INSERT_KNOWLEDGE_BASE_QUERY = """
INSERT INTO herbal_rem.remedy_kb (
    SELECT 
        id,
        symptom,
        safety,
        source,
        timestamp,
        content
    FROM files.herbal_data
);
"""

PROMPT_TEMPLATE = """
SYSTEM:
You are HerbAI, a knowledgeable herbal remedy advisor specialized in natural treatments and traditional medicine.
Your role is to provide accurate, safe, and practical information about herbal remedies.

Guidelines:
1. Always include safety warnings and contraindications
2. Mention potential drug interactions
3. Specify if the remedy is safe during pregnancy
4. Include preparation instructions
5. List any side effects
6. Provide dosage recommendations when possible

Format your response in plain text with clear sections:
- Remedy Name
- Target Symptoms
- Safety Information
- Preparation Method
- Dosage
- Warnings & Interactions
- Source/Origin

If you're unsure about any information, clearly state that and recommend consulting a healthcare professional.
"""

CREATE_AGENT_QUERY = """
CREATE AGENT IF NOT EXISTS herbal_rem.remedy_agent
USING
    model = 'gemini-2.0-flash',
    google_api_key = '{google_api_key}',
    include_knowledge_bases= ['herbal_rem.remedy_kb'],
    prompt_template='{prompt_template}';
""".format(
    google_api_key=getenv("GOOGLE_API_KEY"), prompt_template=PROMPT_TEMPLATE.strip().replace("'", "''")
)
# print(CREATE_AGENT_QUERY)
SELECT_ANSWER_QUERY = """
SELECT answer
FROM herbal_rem.remedy_agent 
WHERE question = '{question}';
"""

CREATE_JOB_PAYLOAD = {
    "name": "daily_herbal_summary",
    "query": """
        SELECT answer
        FROM herbal_rem.remedy_agent
        WHERE question = 'Give me a daily summary of new herbal remedies added.';
    """,
    # Optional: Only run if there are new remedies today
    # "if_query": "SELECT COUNT(*) FROM herbal_rem.remedy_kb WHERE timestamp >= CURDATE();",
    "schedule_str": "0 8 * * *"  # Every day at 8am (cron format)
}
