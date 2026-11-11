import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment (API keys, etc.)
load_dotenv()

# Make project/ importable from one level up
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "project"))
from smart_desk_ai_agent import build_support_agent, ask  # noqa: E402

import gradio as gr  # UI

# Build the agent pipeline once at startup
print("Building Smart Desk Ai Agent UI...")
agent = build_support_agent(collection_name="smartdesk_demo")
app = agent["app"]
print("Pipeline ready. Open the UI to interact.\n")


def run_query(query: str, thread_id: str | None = None):
    # Validate required inputs and raise UI errors for visibility
    if not query or not str(query).strip():
        raise gr.Error("Question is required. Please enter your question.")
    if not thread_id or not str(thread_id).strip():
        raise gr.Error("Thread ID is required. Please enter a Thread ID (e.g., cust-A).")

    result = ask(app, query, thread_id=thread_id)
    response = result.get("response", "")
    intent = result.get("intent", "")
    sources = ", ".join(result.get("retrieved_sources", []) or [])
    return (response, intent, sources)


def build_ui():
    # Apply a dark theme via built-in theme plus CSS overrides
    theme = gr.themes.Soft()
    css = """
    body, .gradio-container { background-color: #0b0f19 !important; color: #e5e7eb !important; }
    .gradio-container .block, .gradio-container .panel, .gradio-container .tabs, .gradio-container .form { background-color: #0b0f19 !important; }
    /* Ensure Markdown content is readable on dark backgrounds */
    .gr-markdown, .gr-markdown * { color: #e5e7eb !important; }
    .prose, .prose :where(p, li, strong, em, code) { color: #e5e7eb !important; }
    .prose h1, .prose h2, .prose h3, .prose h4 { color: #f9fafb !important; }
    .prose a { color: #60a5fa !important; }
    .prose code { background-color: #0b1220 !important; color: #f59e0b !important; }
    .prose pre { background-color: #0b1220 !important; color: #e5e7eb !important; border: 1px solid #374151 !important; }
    textarea, input, .gr-textbox textarea, .gr-textbox input { background-color: #111827 !important; color: #e5e7eb !important; border-color: #374151 !important; }
    .gr-button { background-color: #1f2937 !important; color: #e5e7eb !important; border-color: #374151 !important; }
    .gr-button:hover { background-color: #374151 !important; }
    """
    with gr.Blocks(title="Smart Desk AI Agent", theme=theme, css=css) as demo:
        gr.Markdown("# Smart Desk AI Agent\nAsk questions about HR/IT or tickets.")

        with gr.Row():
            query = gr.Textbox(
                label="Your question (required)",
                placeholder="e.g., Give me the status for Ticket Id --> TICK-002",
                lines=2,
            )
        with gr.Row():
            thread = gr.Textbox(
                label="Thread ID (required)",
                placeholder="e.g., cust-A (use the same ID for follow-ups)",
            )
        ask_btn = gr.Button("Ask")

        # Response label (placed after the Ask button and before the response output)
        with gr.Row():
            gr.Markdown("### Response")
        with gr.Row():
            response = gr.Markdown(label="Response")
        with gr.Row():
            intent = gr.Textbox(label="Detected intent", interactive=False)
            sources = gr.Textbox(label="Retrieved sources", interactive=False)

        # Wire interactions
        ask_btn.click(run_query, inputs=[query, thread], outputs=[response, intent, sources])
        query.submit(run_query, inputs=[query, thread], outputs=[response, intent, sources])
        thread.submit(run_query, inputs=[query, thread], outputs=[response, intent, sources])

        # Quick examples (query only; set thread ID yourself for multi-convo)
        gr.Examples(
            examples=[
                "Give me the status for Ticket created for marry.smith@gmail.com",
                "Give me the description and priority for that Ticket",
                "How do I reset my payroll password?",
            ],
            inputs=query,
        )
    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
