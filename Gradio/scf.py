import gradio as gr
import math

def getSCF(number):
    sq = number * number
    cb = sq * number
    fc = math.factorial(number)
    return str([sq, cb, fc])

demo = gr.Interface(
    fn=getSCF,
    inputs="number",
    outputs=["textbox"]
)

demo.launch(share=True)