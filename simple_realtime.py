"""
Simple real-time sync system using polling instead of WebSockets
More stable and reliable for production use
"""

import json
import time
from flask import jsonify, request
from datetime import datetime, timedelta

class SimpleRealTimeSync:
    def __init__(self):
        self.last_update_time = time.time()
        self.content_changes = []
        self.max_changes_stored = 100
        
    def register_content_change(self, key, value, admin_username=None):
        """Register a content change"""
        change = {
            'key': key,
            'value': value,
            'timestamp': time.time(),
            'admin_username': admin_username or 'System',
            'id': len(self.content_changes)
        }
        
        self.content_changes.append(change)
        self.last_update_time = time.time()
        
        # Keep only recent changes
        if len(self.content_changes) > self.max_changes_stored:
            self.content_changes = self.content_changes[-self.max_changes_stored:]
    
    def get_recent_changes(self, since_timestamp=None):
        """Get content changes since a specific timestamp"""
        if since_timestamp is None:
            since_timestamp = time.time() - 300  # Last 5 minutes
        
        recent_changes = [
            change for change in self.content_changes
            if change['timestamp'] > since_timestamp
        ]
        
        return {
            'changes': recent_changes,
            'last_update': self.last_update_time,
            'timestamp': time.time()
        }
    
    def has_updates(self, since_timestamp):
        """Check if there are updates since timestamp"""
        return self.last_update_time > since_timestamp
    
    def register_routes(self, app):
        """Register polling routes with the Flask app"""
        
        @app.route('/api/realtime/poll')
        def poll_for_updates():
            """Polling endpoint for content updates"""
            since = request.args.get('since', type=float)
            if since is None:
                since = time.time() - 60  # Default to last minute
            
            try:
                updates = self.get_recent_changes(since)
                return jsonify({
                    'success': True,
                    'data': updates
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @app.route('/api/realtime/status')
        def realtime_status():
            """Get real-time sync status"""
            return jsonify({
                'success': True,
                'status': 'active',
                'last_update': self.last_update_time,
                'changes_count': len(self.content_changes)
            })

# Global instance
simple_realtime = SimpleRealTimeSync()

def init_simple_realtime(app):
    """Initialize simple real-time sync with Flask app"""
    simple_realtime.register_routes(app)
    return simple_realtime