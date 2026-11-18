import gradio as gr
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from resumeai.document_loader import load_resume, load_job_description
from resumeai.rag_pipeline import ResumeRAG
from resumeai.prompts import ANALYSIS_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def analyze(resume_file, jd_file, model_name):

    api_key = GROQ_API_KEY

    if not api_key:
        raise gr.Error("Groq API key not found. Please check your .env file.")

    if not resume_file or not jd_file:
        raise gr.Error("Please upload both documents.")

    try:
        resume_text = load_resume(resume_file)
        jd_text = load_job_description(jd_file)

        if len(resume_text.strip()) < 80:
            raise ValueError("Could not extract enough text from resume.")

        if len(jd_text.strip()) < 50:
            raise ValueError("Could not extract enough text from job description.")

        rag = ResumeRAG(
            resume_text=resume_text,
            jd_text=jd_text,
            api_key=api_key,
            model_name=(model_name or GROQ_MODEL).strip()
        )

        result = rag.analyze()

        report = result + "\n\n---\n*This is an AI-generated advisory assessment.*"

        greeting = [{
            "role": "assistant",
            "content": "I've analyzed your resume against the job description. Ask me anything about your results!"
        }]

        return report, rag, greeting

    except Exception as e:
        raise gr.Error(f"Analysis failed: {e}")

def chat(message, history, rag):
    if not rag:
        history = history or []
        history.append({"role": "assistant", "content": "Please upload your resume and job description and click **Analyze documents** first."})
        return "", history
    if not message or not message.strip():
        return "", history
    try:
        answer = rag.ask(message.strip())
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        return "", history
    except Exception as e:
        history = history or []
        history.append({"role": "assistant", "content": f"Sorry, I couldn't answer that: {e}"})
        return "", history

with gr.Blocks(title="ResumeAI — GenAI Resume Analyzer") as demo:
    gr.Markdown(
        """
        # 📄 ResumeAI — GenAI Resume Analyzer & Job Matcher
        Upload a resume and a job description to get an evidence-based match assessment,
        actionable improvement suggestions, and a RAG-powered chatbot.
        """
    )
    with gr.Row():
        with gr.Column(scale=1):
            resume_input = gr.File(
                label="Upload Resume (PDF or DOCX)",
                file_types=[".pdf", ".docx"],
                type="filepath"
            )
            jd_input = gr.File(
                label="Upload Job Description (PDF or TXT)",
                file_types=[".pdf", ".txt"],
                type="filepath"
            )

            model_input = gr.Textbox(
                label="Groq model",
                value=GROQ_MODEL,
                info="You can change this to another model available in your Groq account."
            )
            analyze_btn = gr.Button("✨ Analyze documents", variant="primary")
        with gr.Column(scale=2):
            report_output = gr.Markdown(label="Resume analysis")
    rag_state = gr.State(None)
    chat_history = gr.Chatbot(label="Chat with your resume", height=420)
    with gr.Row():
        chat_input = gr.Textbox(
            label="Ask ResumeAI",
            placeholder="e.g. Which important skills from this JD are missing in my resume?",
            scale=5
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)
    clear_btn = gr.Button("Clear chat")

    analyze_btn.click(
    fn=analyze,
    inputs=[resume_input, jd_input, model_input],
    outputs=[report_output, rag_state, chat_history]
)
    send_btn.click(fn=chat, inputs=[chat_input, chat_history, rag_state], outputs=[chat_input, chat_history])
    chat_input.submit(fn=chat, inputs=[chat_input, chat_history, rag_state], outputs=[chat_input, chat_history])
    clear_btn.click(lambda: [], outputs=chat_history)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
