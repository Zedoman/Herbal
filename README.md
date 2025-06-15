# 🌿 Herbal Remedy AI Knowledge Base 🧠✨

> "Because your grandma’s tea deserves LLM-level respect!"
> 🔮 Powered by MindsDB, Ollama, and Flask. Built with love & curiosity.

---

## 📜 Overview

This project is an AI-powered **Herbal Remedy Search Engine**. Think of it as the ChatGPT of age-old grandma medicine, now equipped with semantic search and knowledge bases.

It supports:

* ⚙️ Ollama integration via MindsDB ML Engine
* 🧠 AI-augmented Knowledge Base querying
* 🗂️ Inserting and browsing herbal remedies
* 🔍 Semantic search for herbal treatments based on symptoms & safety
* ⚖️ Full Flask backend, templated frontend

---

## 🚀 Features

* 💬 Semantic search using `semantic_search` on content
* 🌱 Knowledge Base setup with `ollama_engine` in MindsDB
* 📆 Sample remedies like Ginger Tea for Headaches 🍵
* 📄 Dynamic metadata: symptoms, safety, sources, timestamps
* 🧪 Easily extendable with efficacy ratings
* 💻 Fully server-rendered with `browse`, `add`, and `search` pages

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
Use the form to search herbal remedies using natural language.

### 🔍 `/browse`

Shows top 100 records from the knowledge base in a simple interface.

### ➕ `/add`

Insert your favorite remedy for **cold**, **cough**, or even **existential dread**.

---

## 🗂️ Project Structure

```bash
herbal-remedy-kb-ai/
│
├── templates/
│   ├── search.html
│   ├── browse.html
│   └── add.html
│
├── app.py             # Main Flask server with routes
├── pyproject.toml     # Project config for uv / poetry
├── README.md          # This file 👌
```

---

## 📋 Environment Variables (Optional)

Set this for secure Flask sessions:

```bash
export FLASK_SECRET_KEY="supersecretkey"
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
