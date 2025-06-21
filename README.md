# 🌿 Herbal Remedy Advisor

> "Because your grandma’s tea deserves LLM-level respect!"
> 🔮 Powered by MindsDB, Ollama, and Flask. Built with love & curiosity.

---

## 📜 Overview

This project is an AI-powered **Herbal Remedy Search Engine**. Think of it as the ChatGPT of age-old grandma medicine, now equipped with semantic search and knowledge bases.

It supports:

- 🔍 **Semantic Search**: Find herbal remedies using natural language queries, powered by a knowledge base with embeddings and relevance filtering.
- ➕ **Add Remedy**: Contribute your own herbal wisdom to the community.
- 🌱 **Browse All Remedies**: Explore the full database of natural treatments.
- 🤖 **Ask HerbAI**: Chat with an AI agent for instant, friendly advice on remedies, safety, and more.
- ⚡ **Fast Search**: Uses `CREATE INDEX ON KNOWLEDGE_BASE` for optimized semantic search performance.
- 🛡️ **Safety Info**: Every remedy includes safety, pregnancy, and interaction warnings.
- ✨ **Modern UI**: Beautiful, responsive cards and layout.

---


https://github.com/user-attachments/assets/77a44ae4-f736-4ae2-aab9-c1dd1e25b88c


---

## 🧠 Powered By

| Stack Component | Tech Used                                                  |
| --------------- | ---------------------------------------------------------- |
| **LLM**         | gemini-2.0-flash (for agent chat)                         |
| **Embeddings**  | deepseek-r1:1.5b (Ollama)                                 |
| **DB**          | MindsDB                                                   |
| **Framework**   | [MindsDB](https://mindsdb.com/)                           |
| **Web**         | Flask, Bootstrap 5                                        |

---

## 🔧 Installation Guide (with `uv` magic) 🦨

This project uses [`uv`](https://github.com/astral-sh/uv) for managing dependencies from `pyproject.toml` instead of the usual `pip` dance.

### 1. 🧪 Clone this wisdom:

```bash
git https://github.com/Zedoman/Herbal.git
cd Herbal
```

### 2. ✨ Create virtualenv & install dependencies with `uv`:

```bash
uv venv  # creates .venv and activates it
uv pip install -r <(uv pip compile pyproject.toml --extra=dev)
```

Or go full wizard-mode:

```bash
uv pip install .  # Install from pyproject.toml automatically
```

### 3. 🧠 Run MindsDB locally

Make sure MindsDB is running on port `47334`.

```bash
docker run -p 47334:47334 mindsdb/mindsdb
```

Or install via CLI if you're hardcore:

```bash
pip install mindsdb
mindsdb
```

### 4. 🤖 Run Ollama (locally)

Install [Ollama](https://ollama.com/download) and pull your model:

```bash
ollama run deepseek-r1:1.5b
```

Make sure it's available at `http://localhost:11434`

---

## 🧠 Initialize the System

When the app runs for the first time, it:

* Creates an `ollama_engine` in MindsDB
* Sets up a `herbal_remedy_kb` knowledge base
* Inserts sample herbal data for immediate zen

✅ You’ll see logs like:

```
✅ Ollama ML Engine created
✅ Knowledge Base created with Ollama
✅ Sample data inserted
```

---

## 🧪 Usage

### 🏠 Homepage

Go to `http://localhost:5001`

### 🔍 `/browse`
Use the form to search herbal remedies using natural language.

### 🌱 `/browse`

Shows top 100 records from the knowledge base in a simple interface.

### ➕ `/add`

Insert your favorite remedy for **cold**, **cough**, or even **existential dread**.

### 🤖 `/agent`

Ask your herbal agent anything.

### 🤖 `/create_job`
To create job

---

## 🗂️ Project Structure

```bash
herbal-remedy-kb-ai/
│
├── templates/
│   ├── search.html
│   ├── browse.html
│   ├── agent_status.html
│   ├── index.html
│   ├── base.html
│   └── add.html
├── src/core
│   ├── queries.py
│
├── app.py             # Main Flask server with routes
├── pyproject.toml     # Project config for uv / poetry
├── README.md          # This file 👌
```

---

## 📋 Environment Variables

Set this for secure Flask sessions:

```bash
OLLAMA_SERVE_URL=http://host.docker.internal:11434
OLLAMA_MODEL_NAME=deepseek-r1:1.5b
GOOGLE_API_KEY=
```

---

## 🧑‍🎓 Sample Data

```text
"Headache" → "Ginger tea may help relieve headaches"
"Cold" → "Tulsi leaves brewed in tea help with congestion"
```

---

## 🧪 Example Semantic Search SQL

```sql
SELECT *
FROM herbal_remedy_kb
WHERE semantic_search('headache relief', content)
  AND symptom = 'Headache'
  AND safety LIKE '%Safe%'
LIMIT 20;
```

---

## 📦 Tech Stack

| Layer         | Stack                            |
| ------------- | -------------------------------- |
| 💻 Backend    | Flask + Jinja2                   |
| 🧠 AI Layer   | MindsDB + Ollama (DeepSeek 1.5B) |
| 🗃️ DB Engine | MindsDB-native Knowledge Base    |
| ⚗️ Dev Tool   | `uv` for dependency management   |

---

## ❤️ Acknowledgements

* 🧠 [MindsDB](https://mindsdb.com/) – Making ML as easy as SQL
* 🤖 [Ollama](https://ollama.com/) – Local LLMs that *just work*
* 🧪 [uv](https://github.com/astral-sh/uv) – The Python package manager we deserve

---

## 🦻 Developer Notes

* Got errors like `table doesn't exist`? Restart the server—it auto-creates everything on init.
* Want to reset? Just nuke and relaunch. KBs are created on each fresh start.
* Add more safety levels, metadata tags, or GPTs—this KB is born to scale.

---

## 🧝‍♂️ Final Words

If your grandma's herbal wisdom deserves a SQL interface and AI integration...
**This is it.**
