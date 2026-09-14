"""
Bangla Regional Dialect -> Standard Bengali Translator
A simple Gradio web interface for the finalized BanglaT5 dialect translation model.

SETUP (run once):
    pip install gradio transformers torch sentencepiece

BEFORE RUNNING:
    Replace MODEL_PATH below with either:
      - a Hugging Face Hub model name, e.g. "your-username/banglat5-dialect-to-standard"
        (see Section 4 of Web_Interface_Requirements.md for how to upload the model there), or
      - a local folder path if the saved model files are on this same machine,
        e.g. "./banglat5_final_outputs/banglat5_model"

RUN:
    python app.py
    Then open the local URL that gets printed (usually http://127.0.0.1:7860)
"""

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------------------------------------------------------
# 1. Configuration -- EDIT THIS LINE
# ---------------------------------------------------------------
MODEL_PATH = "your-username/banglat5-dialect-to-standard"  # <-- CHANGE ME

REGIONS = [
    "Pabna",
    "Noakhali",
    "Jashore",
    "Rangpur",
    "Mymensingh",
    "Barishal",
    "Chittagong",
]

MAX_SOURCE_LEN = 40
MAX_TARGET_LEN = 32
NUM_BEAMS = 4  # selected via validation during model development -- do not change without reason

# A few example sentences per region so users can try the demo without typing (optional, edit freely)
EXAMPLES = [
    ["Chittagong", "ক্যান আছু?"],
    ["Noakhali", "তুই কই যাস?"],
    ["Barishal", "মুই বাড়িত যামু"],
]

# ---------------------------------------------------------------
# 2. Load model once at startup (not on every request)
# ---------------------------------------------------------------
print(f"Loading model from: {MODEL_PATH} ...")
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device).eval()

print(f"Model loaded successfully on device: {device}")

# ---------------------------------------------------------------
# 3. Translation function
# ---------------------------------------------------------------
def translate(region: str, dialect_sentence: str) -> str:
    if not dialect_sentence or not dialect_sentence.strip():
        return "Please type a sentence before clicking Translate."

    if not region:
        return "Please select a region."

    # This exact prefix format is required -- the model was trained on it and
    # will not work correctly with a different phrasing (see Section 2 of
    # Web_Interface_Requirements.md).
    input_text = f"translate {region} to Bangla: {dialect_sentence.strip()}"

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_SOURCE_LEN,
    ).to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_TARGET_LEN,
            num_beams=NUM_BEAMS,
            length_penalty=1.0,
            early_stopping=True,
        )

    translated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return translated_text


# ---------------------------------------------------------------
# 4. Build the Gradio interface
# ---------------------------------------------------------------
with gr.Blocks(title="Bangla Dialect Translator") as demo:
    gr.Markdown(
        "# Bangla Regional Dialect \u2192 Standard Bengali Translator\n"
        "Select a region, type a sentence in that dialect, and click **Translate**."
    )

    with gr.Row():
        with gr.Column():
            region_input = gr.Dropdown(
                choices=REGIONS,
                label="Region",
                value=REGIONS[0],
            )
            sentence_input = gr.Textbox(
                label="Dialect sentence",
                placeholder="Type a sentence in the selected region's dialect...",
                lines=3,
            )
            translate_button = gr.Button("Translate", variant="primary")

        with gr.Column():
            output_box = gr.Textbox(
                label="Standard Bengali translation",
                lines=3,
                interactive=False,
            )

    translate_button.click(
        fn=translate,
        inputs=[region_input, sentence_input],
        outputs=output_box,
    )

    # Also allow pressing Enter in the text box to translate
    sentence_input.submit(
        fn=translate,
        inputs=[region_input, sentence_input],
        outputs=output_box,
    )

    if EXAMPLES:
        gr.Examples(
            examples=EXAMPLES,
            inputs=[region_input, sentence_input],
        )

if __name__ == "__main__":
    demo.launch()
