

import os
from dotenv import load_dotenv
import openai
from transformers import pipeline

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_flashcards(text, model="OpenAI GPT-3.5"):
    if model == "OpenAI GPT-3.5":
        prompt = (
            "From the following programming notes, generate a list of flashcards.\n"
            "Each flashcard should have a question and an answer.\n"
            "Respond in the format:\n"
            "Q: [Question text]\nA: [Answer text]\n---\n\n"
            f"{text}"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.5,
            )
            output = response['choices'][0]['message']['content']
            return parse_flashcards(output)
        except Exception as e:
            return [{"question": "Error", "answer": str(e)}]

    elif model == "HuggingFace T5-Small":
        try:
            summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
            result = summarizer(text, max_length=200, min_length=40, do_sample=False)
            summary = result[0]['summary_text']
            return [{
                "question": "Summarize the notes in a sentence?",
                "answer": summary
            }]
        except Exception as e:
            return [{"question": "Error", "answer": str(e)}]

    else:
        return [{"question": "Invalid model selected.", "answer": ""}]

def parse_flashcards(text):
    cards = []
    sections = text.strip().split("---")
    for section in sections:
        lines = section.strip().split("\n")
        q = next((line[2:].strip() for line in lines if line.startswith("Q:")), None)
        a = next((line[2:].strip() for line in lines if line.startswith("A:")), None)
        if q and a:
            cards.append({"question": q, "answer": a})
    return cards