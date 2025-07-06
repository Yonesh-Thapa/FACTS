"""
Advanced Admin Portal for Live Website Editing
Real-time content management system with instant updates
"""

import json
import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import SiteSetting, Admin
import logging

# Create admin portal blueprint
admin_portal = Blueprint('admin_portal', __name__, url_prefix='/admin')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentVersionManager:
    """Manages content versions and rollback functionality"""
    
    def __init__(self):
        self.version_file = 'data/content_versions.json'
        self.ensure_version_file()
    
    def ensure_version_file(self):
        """Ensure version file exists"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.version_file):
            with open(self.version_file, 'w') as f:
                json.dump([], f)
    
    def create_version(self, content_data, admin_id, action):
        """Create a new version snapshot"""
        version = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'admin_id': admin_id,
            'action': action,
            'content': content_data
        }
        
        # Load existing versions
        with open(self.version_file, 'r') as f:
            versions = json.load(f)
        
        # Add new version
        versions.append(version)
        
        # Keep only last 50 versions
        versions = versions[-50:]
        
        # Save back to file
        with open(self.version_file, 'w') as f:
            json.dump(versions, f, indent=2)
        
        logger.info(f"Created version {version['id']} by admin {admin_id}")
        return version['id']
    
    def get_versions(self):
        """Get all content versions"""
        with open(self.version_file, 'r') as f:
            return json.load(f)
    
    def rollback_to_version(self, version_id, admin_id):
        """Rollback to a specific version"""
        versions = self.get_versions()
        target_version = None
        
        for version in versions:
            if version['id'] == version_id:
                target_version = version
                break
        
        if not target_version:
            raise ValueError(f"Version {version_id} not found")
        
        # Apply the version content
        content = target_version['content']
        self.apply_content_to_database(content)
        
        # Create new version for rollback
        self.create_version(content, admin_id, f"Rollback to version {version_id}")
        
        logger.info(f"Rolled back to version {version_id} by admin {admin_id}")
        return True
    
    def apply_content_to_database(self, content):
        """Apply content data to database"""
        for item in content:
            setting = SiteSetting.query.filter_by(key=item['key']).first()
            if setting:
                setting.value = item['value']
                setting.updated_at = datetime.utcnow()
            else:
                setting = SiteSetting(
                    key=item['key'],
                    value=item['value'],
                    category=item.get('category', 'general'),
                    description=item.get('description', '')
                )
                db.session.add(setting)
        
        db.session.commit()

# Initialize version manager
version_manager = ContentVersionManager()

@admin_portal.route('/live-editor')
@login_required
def live_editor():
    """Main live editor interface"""
    return render_template('admin/live_editor.html')

@admin_portal.route('/api/content/get')
@login_required
def get_content():
    """Get all site content for editing"""
    try:
        settings = SiteSetting.query.all()
        content = []
        
        for setting in settings:
            content.append({
                'key': setting.key,
                'value': setting.value,
                'category': setting.category,
                'description': setting.description,
                'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'content': content
        })
    
    except Exception as e:
        logger.error(f"Error getting content: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_portal.route('/api/content/update', methods=['POST'])
@login_required
def update_content():
    """Update content with instant live sync"""
    try:
        data = request.get_json()
        
        if not data or 'updates' not in data:
            return jsonify({
                'success': False,
                'error': 'No updates provided'
            }), 400
        
        updates = data['updates']
        updated_items = []
        
        # Process each update
        for update in updates:
            key = update.get('key')
            value = update.get('value')
            
            if not key:
                continue
            
            # Find or create setting
            setting = SiteSetting.query.filter_by(key=key).first()
            if setting:
                old_value = setting.value
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = SiteSetting(
                    key=key,
                    value=value,
                    category=update.get('category', 'general'),
                    description=update.get('description', '')
                )
                db.session.add(setting)
                old_value = None
            
            updated_items.append({
                'key': key,
                'old_value': old_value,
                'new_value': value
            })
        
        # Commit all changes
        db.session.commit()
        
        # Create version snapshot
        all_settings = SiteSetting.query.all()
        content_snapshot = [
            {
                'key': s.key,
                'value': s.value,
                'category': s.category,
                'description': s.description
            }
            for s in all_settings
        ]
        
        version_id = version_manager.create_version(
            content_snapshot, 
            current_user.id, 
            f"Updated {len(updated_items)} items"
        )
        
        logger.info(f"Updated {len(updated_items)} content items by admin {current_user.id}")
        
        return jsonify({
            'success': True,
            'updated_items': updated_items,
            'version_id': version_id,
            'message': f'Successfully updated {len(updated_items)} items'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating content: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_portal.route('/api/content/versions')
@login_required
def get_versions():
    """Get content version history"""
    try:
        versions = version_manager.get_versions()
        
        # Add admin usernames to versions
        for version in versions:
            admin = Admin.query.get(version['admin_id'])
            version['admin_username'] = admin.username if admin else 'Unknown'
        
        return jsonify({
            'success': True,
            'versions': versions
        })
    
    except Exception as e:
        logger.error(f"Error getting versions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_portal.route('/api/content/rollback', methods=['POST'])
@login_required
def rollback_content():
    """Rollback to a specific version"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({
                'success': False,
                'error': 'Version ID required'
            }), 400
        
        version_manager.rollback_to_version(version_id, current_user.id)
        
        return jsonify({
            'success': True,
            'message': f'Successfully rolled back to version {version_id}'
        })
    
    except Exception as e:
        logger.error(f"Error rolling back: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_portal.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file uploads for content editing"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            # Ensure upload directory exists
            upload_dir = 'static/uploads'
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Return URL for use in content
            file_url = f"/static/uploads/{filename}"
            
            logger.info(f"File uploaded: {filename} by admin {current_user.id}")
            
            return jsonify({
                'success': True,
                'filename': filename,
                'url': file_url
            })
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Register the blueprint
def register_admin_portal(app):
    """Register the admin portal blueprint with the main app"""
    app.register_blueprint(admin_portal)