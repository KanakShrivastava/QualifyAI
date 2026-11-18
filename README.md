# ResumeAI — GenAI Resume Analyzer & Job Matcher

A Gradio application that compares a resume with a job description using a retrieval-augmented generation (RAG) pipeline.

## Features

- Resume upload: PDF or DOCX
- Job description upload: PDF or TXT
- Text extraction from PDF, Word and TXT files
- Chunking and semantic embeddings with Sentence Transformers
- FAISS vector search for retrieval
- Groq-hosted LLM for analysis and chat
- Estimated resume–JD match score with a transparent rubric
- Strong matches, missing/weakly demonstrated requirements, keyword guidance and improvement plan
- RAG chatbot for follow-up questions

## Architecture

```text
Resume (PDF/DOCX) ----> Text extraction ----\
                                             \
                                              -> Chunking -> SentenceTransformer
                                             /                    |
Job Description (PDF/TXT) -> Text extraction /                     v
                                                               FAISS index
                                                                   |
User question / analysis request -> Query embedding -> Similarity retrieval
                                                                   |
                                                                   v
                                                     Retrieved resume + JD context
                                                                   |
                                                                   v
                                                        Groq LLM + prompts
                                                                   |
                                                                   v
                                                   Analysis report / chatbot answer
                                                                   |
                                                                   v
                                                              Gradio UI
```

## 1. Requirements

- Python 3.10 or 3.11 recommended
- Internet connection for the first model download and Groq API calls
- Groq API key: https://console.groq.com/keys

## 2. Open the project in VS Code

Extract the ZIP file, then open the `ResumeAI_GenAI_Chatbot` folder in VS Code.

Open the VS Code terminal (`Terminal > New Terminal`).

## 3. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\\Scripts\\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`sentence-transformers` downloads the `all-MiniLM-L6-v2` embedding model the first time it runs. This may take a few minutes.

## 5. Run the app

```bash
python app.py
```

Open the local Gradio URL printed in the terminal (usually http://127.0.0.1:7860).

## 6. Use the chatbot

1. Upload a resume in PDF or DOCX format.
2. Upload the job description in PDF or TXT format.
3. Paste your Groq API key into the password field.
4. Click **Analyze documents**.
5. Read the match score, strong matches, gaps, keyword suggestions and action plan.
6. Ask follow-up questions in the chatbot.

Example questions:

- Which required skills are missing from my resume?
- Which three changes would improve my match the most?
- Rewrite my project description for this job, without inventing details.
- Which keywords are already supported by my experience?
- Is my work experience relevant to this role?
- Suggest a stronger professional summary based only on my resume.

## How the score works

The model is instructed to use this weighted rubric:

| Criterion | Weight |
|---|---:|
| Required skills and tools | 30 |
| Relevant experience and responsibilities | 25 |
| Projects and evidence | 20 |
| Education and qualifications | 10 |
| Role-specific keywords | 10 |
| Clarity and relevance | 5 |
| **Total** | **100** |

This is an AI-generated advisory estimate. It is not an official ATS score, and different employers use different screening systems.

## Project structure

```text
ResumeAI_GenAI_Chatbot/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── resumeai/
    ├── __init__.py
    ├── document_loader.py
    ├── prompts.py
    └── rag_pipeline.py
```

## Important notes

- The app processes uploaded files for the current session. It does not permanently save resumes or job descriptions.
- The FAISS index is built in memory for each analysis session.
- Scanned/image-only PDFs may not contain extractable text. Run OCR on those files before uploading.
- Never commit your API key or `.env` file to GitHub.
- Do not add skills, experience, achievements or numerical results to a resume unless they are true and can be verified.
- The model name is configurable in the UI. If the default model is unavailable in your Groq account, enter a currently supported chat model name from your Groq console.

## Troubleshooting

**`ModuleNotFoundError`**
Activate the virtual environment and run `pip install -r requirements.txt` again.

**Groq authentication error**
Check that the API key is valid and has not been revoked.

**Model not found / unavailable**
Change the model name in the Gradio UI to a model currently available to your Groq account.

**PDF text is empty**
The PDF may be scanned. Use OCR to convert it into a text-searchable PDF first.

**FAISS / package installation issue on Windows**
Use Python 3.10 or 3.11 in a fresh virtual environment and upgrade pip before installing dependencies.
