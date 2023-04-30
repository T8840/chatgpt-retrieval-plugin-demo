from typing import Any, List, Dict
import openai
import requests
import os
from database_utils import query_database
import logging



def apply_prompt_template(question: str) -> str:
    """
        A helper function that applies additional template on user's question.
        Prompt engineering could be done here to improve the result. Here I will just use a minimal example.
    """
    prompt = f"""
        By considering above input from me, answer the question: {question}
    """
    return prompt


def call_chatgpt_api(user_question: str, chunks: List[str]) -> Dict[str, Any]:
    """
    Call chatgpt api with user's question and retrieved chunks.
    """
    # Send a request to the GPT-3 API
    messages = list(
        map(lambda chunk: {
            "role": "user",
            "content": chunk
        }, chunks))
    question = apply_prompt_template(user_question)
    messages.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,  # High temperature leads to a more creative response.
    )
    return response


def ask(user_question: str, source_id : str = None) -> Dict[str, Any]:
    """
    Handle user's questions.
    """
    # Get chunks from database.
    chunks_response = query_database(user_question,source_id=source_id)
    chunks = []
    for result in chunks_response["results"]:
        for inner_result in result["results"]:
            chunks.append(inner_result["text"])

    logging.info("User's questions: %s", user_question)
    logging.info("Retrieved chunks: %s", chunks)

    response = call_chatgpt_api(user_question, chunks)
    logging.info("Response: %s", response)

    return response["choices"][0]["message"]["content"]
