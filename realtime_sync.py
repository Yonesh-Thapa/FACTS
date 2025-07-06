"""
Real-time synchronization system for instant content updates
Uses WebSocket connections for live sync between admin and public site
"""

import json
import asyncio
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

class RealTimeSync:
    def __init__(self, app=None):
        self.socketio = None
        self.active_connections = {}
        self.admin_sessions = set()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize SocketIO with the Flask app"""
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        # Register event handlers
        self.register_handlers()
        
        logger.info("Real-time sync system initialized")
    
    def register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            session_id = request.sid
            self.active_connections[session_id] = {
                'connected_at': asyncio.get_event_loop().time(),
                'user_type': 'guest'
            }
            
            logger.info(f"Client connected: {session_id}")
            emit('connection_established', {'session_id': session_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            session_id = request.sid
            
            if session_id in self.active_connections:
                user_type = self.active_connections[session_id]['user_type']
                del self.active_connections[session_id]
                
                if user_type == 'admin':
                    self.admin_sessions.discard(session_id)
                
                logger.info(f"Client disconnected: {session_id} ({user_type})")
        
        @self.socketio.on('admin_join')
        def handle_admin_join(data):
            """Handle admin joining the editing session"""
            if not current_user.is_authenticated:
                emit('error', {'message': 'Unauthorized'})
                return
            
            session_id = request.sid
            self.active_connections[session_id]['user_type'] = 'admin'
            self.admin_sessions.add(session_id)
            
            join_room('admin_room')
            
            logger.info(f"Admin joined editing session: {current_user.username}")
            emit('admin_joined', {
                'admin_id': current_user.id,
                'admin_username': current_user.username
            }, room='admin_room')
        
        @self.socketio.on('content_update')
        def handle_content_update(data):
            """Handle real-time content updates from admin"""
            if not current_user.is_authenticated:
                emit('error', {'message': 'Unauthorized'})
                return
            
            try:
                # Validate the update data
                if not data or 'updates' not in data:
                    emit('error', {'message': 'Invalid update data'})
                    return
                
                # Process the updates
                processed_updates = []
                for update in data['updates']:
                    if 'key' in update and 'value' in update:
                        processed_updates.append({
                            'key': update['key'],
                            'value': update['value'],
                            'timestamp': asyncio.get_event_loop().time(),
                            'admin_id': current_user.id
                        })
                
                # Broadcast to all connected clients (both admin and public)
                self.socketio.emit('live_content_update', {
                    'updates': processed_updates,
                    'source': 'admin',
                    'admin_username': current_user.username
                })
                
                logger.info(f"Content update broadcast: {len(processed_updates)} changes by {current_user.username}")
                
            except Exception as e:
                logger.error(f"Error processing content update: {str(e)}")
                emit('error', {'message': f'Update failed: {str(e)}'})
        
        @self.socketio.on('request_content_sync')
        def handle_content_sync_request():
            """Handle request for full content synchronization"""
            try:
                # Get current content from database
                from models import SiteSetting
                settings = SiteSetting.query.all()
                
                content_data = []
                for setting in settings:
                    content_data.append({
                        'key': setting.key,
                        'value': setting.value,
                        'category': setting.category,
                        'last_updated': setting.updated_at.isoformat() if setting.updated_at else None
                    })
                
                emit('content_sync_response', {
                    'content': content_data,
                    'timestamp': asyncio.get_event_loop().time()
                })
                
            except Exception as e:
                logger.error(f"Error syncing content: {str(e)}")
                emit('error', {'message': f'Sync failed: {str(e)}'})
        
        @self.socketio.on('preview_refresh')
        def handle_preview_refresh():
            """Handle preview refresh requests"""
            if not current_user.is_authenticated:
                emit('error', {'message': 'Unauthorized'})
                return
            
            # Broadcast refresh signal to all clients
            self.socketio.emit('refresh_preview', {
                'source': 'admin',
                'timestamp': asyncio.get_event_loop().time()
            })
            
            logger.info(f"Preview refresh requested by {current_user.username}")
    
    def broadcast_content_change(self, updates, admin_user):
        """Broadcast content changes to all connected clients"""
        if not self.socketio:
            return
        
        try:
            self.socketio.emit('live_content_update', {
                'updates': updates,
                'source': 'server',
                'admin_username': admin_user.username if admin_user else 'System',
                'timestamp': asyncio.get_event_loop().time()
            })
            
            logger.info(f"Broadcast content change: {len(updates)} updates")
            
        except Exception as e:
            logger.error(f"Error broadcasting content change: {str(e)}")
    
    def notify_admin_sessions(self, message, data=None):
        """Send notification to all admin sessions"""
        if not self.socketio:
            return
        
        try:
            self.socketio.emit('admin_notification', {
                'message': message,
                'data': data or {},
                'timestamp': asyncio.get_event_loop().time()
            }, room='admin_room')
            
        except Exception as e:
            logger.error(f"Error notifying admin sessions: {str(e)}")
    
    def get_connection_stats(self):
        """Get statistics about active connections"""
        admin_count = len(self.admin_sessions)
        guest_count = len(self.active_connections) - admin_count
        
        return {
            'total_connections': len(self.active_connections),
            'admin_sessions': admin_count,
            'guest_sessions': guest_count,
            'active_admins': list(self.admin_sessions)
        }

# Global instance
realtime_sync = RealTimeSync()

# Helper function to initialize with app
def init_realtime_sync(app):
    """Initialize real-time sync with Flask app"""
    realtime_sync.init_app(app)
    return realtime_sync.socketio