"""
Chatbot utilities for the Future Accountants website
"""
import os
from datetime import datetime
import logging

# Create a logger
logger = logging.getLogger(__name__)

# Define common accounting terms and their explanations for the fallback mode
ACCOUNTING_TERMS = {
    "asset": "Resources owned by a business that have future economic value.",
    "liability": "Obligations that a business owes to others, such as loans or accounts payable.",
    "equity": "The residual interest in the assets after deducting liabilities (Owner's stake).",
    "revenue": "Income generated from business activities, typically from selling goods or services.",
    "expense": "Costs incurred in running a business and generating revenue.",
    "journal entry": "A record of a financial transaction in the accounting system.",
    "ledger": "A collection of accounts that shows the changes made to each account as a result of transactions.",
    "trial balance": "A report listing all general ledger accounts and their balances to ensure debits equal credits.",
    "balance sheet": "A financial statement showing a company's assets, liabilities, and equity at a specific point in time.",
    "income statement": "A financial statement showing a company's revenues and expenses over a period of time.",
    "cash flow statement": "A financial statement showing how changes in balance sheet accounts and income affect cash and cash equivalents.",
    "accrual accounting": "An accounting method where revenue and expenses are recorded when they are earned or incurred, regardless of when cash is exchanged.",
    "cash accounting": "An accounting method where revenue and expenses are recorded only when cash is received or paid.",
    "depreciation": "The allocation of the cost of a tangible asset over its useful life.",
    "accounts receivable": "Money owed to a company by its debtors or customers.",
    "accounts payable": "Money a company owes to its creditors or suppliers.",
    "goodwill": "An intangible asset representing the excess of purchase price over the fair market value of assets during an acquisition.",
    "retained earnings": "The cumulative net income that is retained by a corporation rather than distributed to shareholders as dividends.",
    "gross profit": "Revenue minus cost of goods sold.",
    "net profit": "Gross profit minus all expenses including taxes.",
    "audit": "An official inspection of an organization's accounts by an independent body.",
    "cpa": "Certified Public Accountant - a professional designation for qualified accountants.",
    "asa": "Associate of the Society of Accountants - a professional designation in Australia.",
    "xero": "A cloud-based accounting software platform for small and medium-sized businesses.",
    "myob": "Mind Your Own Business - accounting software commonly used in Australia and New Zealand.",
    "bas": "Business Activity Statement - a form submitted to the Australian Taxation Office (ATO).",
    "gst": "Goods and Services Tax - a value-added tax on most goods and services sold in Australia.",
    "payg": "Pay As You Go - a system of paying tax instalments during the income year in Australia.",
    "single entry": "A bookkeeping method that uses only one entry per transaction, rather than the more common double-entry method.",
    "double entry": "A fundamental accounting principle where every transaction affects at least two accounts (debit and credit).",
    "reconciliation": "The process of matching transactions in an account to corresponding transactions in other records.",
}

def get_chatbot_response(question, use_api=True):
    """
    Get a response from the chatbot. If the API is available, use it.
    Otherwise, use a fallback mechanism.
    
    Args:
        question (str): The user's question
        use_api (bool): Whether to attempt to use the OpenAI API
        
    Returns:
        dict: Response with success status and content
    """
    # Log the question
    logger.info(f"Chatbot question received: {question[:50]}...")
    
    # Check if we should try using the API
    if use_api:
        try:
            # Import conditionally to avoid errors if OpenAI isn't configured
            from utils.openai import get_accounting_assistant_response
            
            # Try to get a response from the OpenAI API
            result = get_accounting_assistant_response(question)
            
            # If successful, return the API response
            if result["success"]:
                logger.info("Successfully used OpenAI API for chatbot response")
                return result
        except Exception as e:
            logger.error(f"Error using OpenAI API: {str(e)}")
    
    # Fallback mechanism - simple keyword matching
    return get_fallback_response(question)

def get_fallback_response(question):
    """
    Simple fallback for when the API is not available.
    Uses keyword matching against common accounting terms.
    
    Args:
        question (str): The user's question
        
    Returns:
        dict: Response with success status and content
    """
    # Convert question to lowercase for matching
    question_lower = question.lower()
    
    # Look for matches with accounting terms
    matches = []
    for term, explanation in ACCOUNTING_TERMS.items():
        if term in question_lower:
            matches.append((term, explanation))
    
    # If we found matches, construct a helpful response
    if matches:
        # Sort matches by term length (longest first) to prioritize most specific matches
        matches.sort(key=lambda x: len(x[0]), reverse=True)
        
        # Construct the response
        if len(matches) == 1:
            term, explanation = matches[0]
            response = f"{term.capitalize()}: {explanation}"
        else:
            response = "Here are some explanations for terms in your question:\n\n"
            for term, explanation in matches[:3]:  # Limit to top 3 matches
                response += f"• {term.capitalize()}: {explanation}\n\n"
        
        return {
            "success": True,
            "content": response,
            "source": "fallback"
        }
    
    # No matches found, provide a generic response
    return {
        "success": True,
        "content": "I'm currently operating in limited mode without API access. " + 
                  "I can answer simple questions about accounting terms, but for more " +
                  "complex questions, please try again later when API access is available. " +
                  "You can also contact your instructor for detailed assistance.",
        "source": "fallback"
    }