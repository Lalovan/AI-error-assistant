## AI Error Assistant 🪄 

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)

![Ollama](https://img.shields.io/badge/Ollama-Supported-black?logo=ollama)




At a Glance: AI Error Assistant is a local, Dockerized FastAPI service paired with a **Jupyter ```%%ai``` cell magic** that automatically explains Python errors using an LLM. Instead of copy-pasting code and tracebacks into ChatGPT, errors are captured, sent to an AI backend, and explained immediately inside your development workflow.

## 1. Overview

This project explores how AI can be integrated into developer tooling to improve learning and debugging workflows.

The system consists of:

- a FastAPI backend that receives Python code and error tracebacks and generates structured explanations using a Groq-hosted LLM.

- a Dockerized deployment, making the backend portable and reproducible.

- a Jupyter Notebook ```%%ai``` magic, which executes Python code, intercepts runtime errors, and displays AI explanations inline.

While the project initially experimented with a VS Code extension, the final and most reliable interface is notebook-based, prioritizing low friction, immediate feedback, and learning efficiency.

***NB! The notebook magic captures the Python traceback and source code and sends them to the LLM for explanation. Users should be aware that error messages may contain local file paths, usernames, host names, or other environment information. For sensitive environments, basic sanitization (e.g., path stripping or redaction) is added before sending requests.***


## 2. System Architecture

### **High level flow**

```
+------------------+
| Jupyter Notebook |
|  %%ai cell       |
+--------+---------+
         |
         |  code + traceback
         v
+--------+---------+
| FastAPI Backend  |
|  /analyse        |
+--------+---------+
         |
         |  prompt
         v
+------------------+
| Groq LLM API     |
(llama-3.1-8b-instant)|
+------------------+
         |
         v
+------------------+
| AI Explanation   |
| (inline output)  |
+------------------+

```

### **Components**
1. FastAPI Backend (```app.py```):

- Accepts Python code and error tracebacks via /analyze
- Constructs a structured teaching-oriented prompt
- Calls Groq’s LLM API
- Returns an explanation focused on:
    1. What went wrong
    2. Why it happened
    3. How to fix it
    4. A minimal hint or example
2. Docker:
- Ensures reproducible execution
- Encapsulates dependencies and API configuration
- Makes the backend deployable locally or remotely
3. Jupyter Notebook Magic ```%%ai```:
- Executes Python code inside the notebook
- Automatically intercepts exceptions
- Sends errors to the backend
- Displays AI explanations inline using Markdown

## 3. Create the Dockerfile 
Create a ```Dockerfile``` in the root of your project with content like:

```
# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy Python code and requirements
COPY app.py ./
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Command to run the backend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```


## 4. Installation & Setup

Prerequisites:
Python 3.9+,
Docker,
Groq API key,
Jupyter Notebook or JupyterLab;

1. Clone the Repository
```
git clone https://github.com/Lalovan/AI-error-assistant.git
cd ai-error-assistant
```

2. Configure Environment Variables

Create a ```.env``` file in the project root containing your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```
This key will be used by the FastAPI backend (```app.py```) to call the LLM.

3. Run the Backend
You have two options: Docker (recommended for reproducibility) or directly with uvicorn.

Option A (Docker):
```
# Build the Docker image
docker build -t ai-error-assistant .

# Run the container with environment variables
docker run -p 8000:8000 --env-file .env ai-error-assistant
```

or

Option B (uvicorn):

```
uvicorn app:app --reload

```
The backend (app.py) will now be running at:

```
http://127.0.0.1:8000/analyze
```

Important: The FastAPI service must be running for the notebook magic to work.

4. Use the Jupyter ```%%ai``` Magic
In a Jupyter notebook, run once (including sanitization of sensitive information):
```
import requests
import traceback
from IPython.core.magic import register_cell_magic
from IPython.display import display, Markdown

BACKEND_URL = "http://127.0.0.1:8000/analyze"

@register_cell_magic
def ai(line, cell):
    try:
        exec(cell, globals())
    except Exception:

        # Capture the full traceback
        error_text = traceback.format_exc()

        # Display the original traceback in the notebook
        display(Markdown(f"**Python Error:**\n\n```\n{error_text}\n```"))

        # Sanitize sensitive information before sending to the LLM

        import re

        sanitized_error = re.sub(r"(/home/\S+|/Users/\S+)", "[REDACTED PATH]", error_text)
        sanitized_error = re.sub(r"(\w+\.local)", "[REDACTED HOST]", sanitized_error)

        # Send code + sanitized error to the FastAPI backend
        response = requests.post(
            BACKEND_URL,
            json={"code": cell, "error": sanitized_error}
        )
        analysis = response.json().get("analysis", "No AI explanation returned.")

        # Display AI hint in the notebook
        display(Markdown(f"**AI Hint:**\n\n\n{analysis}\n"))
```

Now you can write in a notebook cell:
```
%%ai
# your code 
```
…and receive an AI guidance inline.


### **Everyday Usage (After Initial Setup)**

Once the backend and magic are installed:
- Start the FastAPI backend (Docker or uvicorn).
- You don’t need to rebuild or reconfigure API keys.
- Open your Jupyter Notebook.
- Run the magic registration cell once (def ai(...)) to enable %%ai.
- Use ```%%ai``` in cells as needed — no further setup is required.
The FastAPI service acts as a persistent AI “brain” — it can stay running while you open new notebooks or restart kernels.


## 5. Why This Is Useful...

**...compared to Copy-Pasting into ChatGPT**

Advantages:

- Zero context switching
- Errors captured automatically
- No manual formatting
- Works repeatedly and consistently
- Fits directly into a learning workflow

Trade-offs:

- One-shot explanations (not conversational)
- Requires backend running

**...compared to a Streamlit App**

Notebook Magic:
- Runs code directly (real execution context)
- Best for learning, experimentation, and debugging
- Programmatic and scriptable
- Minimal UI overhead

Streamlit:
- Better for demos and non-technical users
- Manual copy-paste of code
- No real execution context

This project prioritizes developer learning over presentation.

## 6. Possible Future Improvements

This architecture is intentionally modular. Possible extensions include:
- VS Code extension (already partially explored)
- CLI tool (ai-run file.py)
- Slack or Discord bot
- Web-based editor (Monaco / CodeMirror)
- Batch analysis of student submissions
- Integration into ML / Data Science notebooks for teaching

The FastAPI backend can power all of these without major changes.




