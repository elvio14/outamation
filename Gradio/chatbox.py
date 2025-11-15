import gradio as gr

with gr.Blocks(title="Document Q&A Chatbot") as demo:
    # UI components go here
    pass

with gr.Column(scale=2):
		chatbot = gr.Chatbot(label="Chat History", height=500)
		user_input = gr.Textbox(
			placeholder="Ask a question about your document...",
			label="Your Question"
		)
		send_btn = gr.Button("📤 Send")
                
with gr.Column(scale=1):
    pdf_input = gr.File(label="📄 Upload PDF", file_types=[".pdf"])
    process_btn = gr.Button("🔄 Process Document")
    clear_btn = gr.Button("🗑️ Clear Chat")

# Sample logic functions
def process_pdf(file):
    return "PDF processed successfully!"

def handle_chat(message, history):
    return history + [(message, "This is a mock answer.")]

process_btn.click(process_pdf, inputs=pdf_input, outputs=None)
send_btn.click(handle_chat, inputs=[user_input, chatbot], outputs=chatbot)
user_input.submit(handle_chat, inputs=[user_input, chatbot], outputs=chatbot)
clear_btn.click(lambda: [], outputs=[chatbot])

demo.launch()