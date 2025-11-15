import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

# demo = gr.Interface(
#     fn=greet,
#     inputs=["text", "slider"],
#     outputs="text"
# )

def analyze(text):
    return len(text.split()), text.upper()

demo = gr.Interface(
    fn=analyze,
    inputs="textbox",
    outputs=["number", "textbox"]
)

demo.launch(share=True)