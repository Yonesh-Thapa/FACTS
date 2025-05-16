"""
Chatbot API route to be added to the main app.py file
"""

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """API endpoint for the AI study assistant chatbot"""
    # Check if the request is valid
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Invalid request format. Expected JSON.',
            'content': None
        }), 400
    
    # Get the message from the request
    message = request.json.get('message', '')
    if not message:
        return jsonify({
            'success': False,
            'error': 'No message provided.',
            'content': None
        }), 400
    
    # Log the chatbot request (without storing the full message content for privacy)
    app.logger.info(f"Chatbot request received from {request.remote_addr}")
    
    # Get a response from the chatbot
    has_openai_key = bool(os.environ.get('OPENAI_API_KEY'))
    response = get_chatbot_response(message, use_api=has_openai_key)
    
    # Return the response
    return jsonify(response)