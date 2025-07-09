"""
Performance monitoring and optimization utilities
"""
import time
import functools
from flask import request, g, current_app
from datetime import datetime

class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests': [],
            'database_queries': [],
            'external_api_calls': []
        }
    
    def track_request_time(self, func):
        """Decorator to track request processing time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
            except Exception as e:
                status_code = 500
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                self.metrics['requests'].append({
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'duration': duration,
                    'status_code': status_code,
                    'timestamp': datetime.utcnow()
                })
                
                # Log slow requests
                if duration > 1.0:  # Requests taking more than 1 second
                    current_app.logger.warning(
                        f'Slow request: {request.method} {request.path} took {duration:.2f}s'
                    )
            
            return result
        return wrapper
    
    def get_metrics_summary(self, last_n_minutes=60):
        """Get performance metrics summary"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=last_n_minutes)
        
        recent_requests = [
            r for r in self.metrics['requests'] 
            if r['timestamp'] > cutoff_time
        ]
        
        if not recent_requests:
            return {
                'total_requests': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'slowest_endpoints': []
            }
        
        total_requests = len(recent_requests)
        avg_response_time = sum(r['duration'] for r in recent_requests) / total_requests
        error_count = sum(1 for r in recent_requests if r['status_code'] >= 400)
        error_rate = (error_count / total_requests) * 100
        
        # Group by endpoint for analysis
        endpoint_times = {}
        for request in recent_requests:
            endpoint = request['endpoint']
            if endpoint not in endpoint_times:
                endpoint_times[endpoint] = []
            endpoint_times[endpoint].append(request['duration'])
        
        # Find slowest endpoints
        slowest_endpoints = []
        for endpoint, times in endpoint_times.items():
            avg_time = sum(times) / len(times)
            slowest_endpoints.append({
                'endpoint': endpoint,
                'avg_time': avg_time,
                'request_count': len(times)
            })
        
        slowest_endpoints.sort(key=lambda x: x['avg_time'], reverse=True)
        
        return {
            'total_requests': total_requests,
            'avg_response_time': round(avg_response_time, 3),
            'error_rate': round(error_rate, 2),
            'slowest_endpoints': slowest_endpoints[:5]
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def init_performance_monitoring(app):
    """Initialize performance monitoring for Flask app"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Add performance headers
            response.headers['X-Response-Time'] = f'{duration:.3f}s'
            
            # Log performance metrics
            performance_monitor.metrics['requests'].append({
                'endpoint': request.endpoint,
                'method': request.method,
                'duration': duration,
                'status_code': response.status_code,
                'timestamp': datetime.utcnow(),
                'path': request.path
            })
            
            # Keep only recent metrics (last 1000 requests)
            if len(performance_monitor.metrics['requests']) > 1000:
                performance_monitor.metrics['requests'] = performance_monitor.metrics['requests'][-1000:]
        
        return response
    
    # Add performance monitoring route for admins
    @app.route('/admin/performance')
    def admin_performance():
        from flask_login import login_required
        
        @login_required
        def performance_dashboard():
            metrics = performance_monitor.get_metrics_summary()
            return render_template('admin/performance.html', metrics=metrics)
        
        return performance_dashboard()

# Database query optimization helpers
def optimize_database_queries(app, db):
    """Add database query optimization"""
    
    # Enable query logging in development
    if app.debug:
        import logging
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Add database query tracking
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        
        # Log slow queries
        if total > 0.1:  # Queries taking more than 100ms
            app.logger.warning(f'Slow query: {total:.3f}s - {statement[:100]}...')
        
        # Track query metrics
        performance_monitor.metrics['database_queries'].append({
            'duration': total,
            'statement': statement[:200],  # First 200 chars
            'timestamp': datetime.utcnow()
        })

# Cache optimization
def setup_caching(app):
    """Setup caching for better performance"""
    try:
        from flask_caching import Cache
        
        cache_config = {
            'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        }
        
        if app.config.get('CACHE_TYPE') == 'redis':
            cache_config['CACHE_REDIS_URL'] = app.config.get('REDIS_URL')
        
        cache = Cache()
        cache.init_app(app, config=cache_config)
        
        return cache
        
    except ImportError:
        app.logger.warning('Flask-Caching not installed. Using no cache.')
        return None

# Rate limiting setup
def setup_rate_limiting(app):
    """Setup rate limiting for API endpoints"""
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=[app.config.get('RATELIMIT_DEFAULT', '100 per hour')],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
        )
        
        return limiter
        
    except ImportError:
        app.logger.warning('Flask-Limiter not installed. No rate limiting applied.')
        return None

# Asset optimization
def optimize_static_assets(app):
    """Optimize static asset delivery"""
    
    @app.after_request
    def add_cache_headers(response):
        """Add appropriate cache headers to static files"""
        
        # Cache static files for longer periods
        if request.endpoint == 'static':
            if request.path.endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg')):
                # Cache for 1 year
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            elif request.path.endswith(('.html', '.txt', '.xml')):
                # Cache for 1 hour
                response.headers['Cache-Control'] = 'public, max-age=3600'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add compression headers
        if 'gzip' in request.headers.get('Accept-Encoding', ''):
            if response.mimetype in ['text/html', 'text/css', 'application/javascript', 'application/json']:
                response.headers['Vary'] = 'Accept-Encoding'
        
        return response
