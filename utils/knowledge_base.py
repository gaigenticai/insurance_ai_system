"""Simple knowledge base for the Streamlit chatbot."""

FAQ = {
    "underwriting": "Underwriting assesses risk and determines policy terms.",
    "claims": "Claims processing evaluates and settles policyholder claims.",
    "actuarial": "Actuarial analysis models risk to set premiums and reserves.",
    "documents": "You can upload PDF or image files which are processed with OCR.",
}


def get_answer(question: str) -> str:
    """Return a canned answer from the FAQ based on keyword match."""
    q = question.lower()
    for keyword, answer in FAQ.items():
        if keyword in q:
            return answer
    return "Sorry, I do not have an answer for that question."
