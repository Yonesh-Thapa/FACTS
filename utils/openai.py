import json
import os
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_openai_client():
    """Get OpenAI client or None if API key is not available"""
    if not OPENAI_API_KEY:
        return None
    return OpenAI(api_key=OPENAI_API_KEY)

def chat_completion(prompt, system_message=None, model="gpt-4o"):
    """
    Get a chat completion from the OpenAI API.
    
    Args:
        prompt (str): The user's question
        system_message (str, optional): System message for the AI assistant
        model (str, optional): The model to use. Defaults to "gpt-4o".
        
    Returns:
        dict: Response with success status and content
    """
    client = get_openai_client()
    if not client:
        return {
            "success": False,
            "error": "OpenAI API key not configured. Please contact the administrator.",
            "content": None
        }
    
    try:
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "success": True,
            "error": None,
            "content": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "content": None
        }

def get_accounting_assistant_response(question):
    """
    Get a response from the AI accounting assistant.
    
    Args:
        question (str): The user's accounting-related question
        
    Returns:
        dict: Response with success status and content
    """
    system_message = """
    You are an AI accounting assistant for Future Accountants Coaching and Training Services.
    
    Your role is to assist accounting students with their questions about:
    1. Accounting principles, concepts, and theories
    2. Xero and MYOB software usage
    3. Career advice for accountants
    4. Financial statement preparation
    5. Tax compliance and regulations (primarily Australian)
    6. Cybersecurity in accounting
    
    Keep responses concise (under 250 words) but informative.
    
    For questions outside your knowledge or scope:
    - Acknowledge your limitations
    - Suggest contacting their instructor for specific course-related questions
    - Recommend checking official documentation for advanced software questions
    
    Always maintain a professional, helpful tone appropriate for an educational context.
    """
    
    return chat_completion(question, system_message)