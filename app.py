import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from utils.downloader import TikTokDownloader
import tempfile
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize TikTok downloader
downloader = TikTokDownloader()

# Cleanup old files periodically
def cleanup_old_files():
    """Clean up old downloaded files"""
    try:
        temp_dir = tempfile.gettempdir()
        current_time = time.time()
        for filename in os.listdir(temp_dir):
            if filename.startswith('tiktok_'):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath) and current_time - os.path.getmtime(filepath) > 3600:  # 1 hour
                    os.remove(filepath)
                    logging.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=lambda: [time.sleep(3600), cleanup_old_files()], daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Main page with download form"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    """Handle video download requests"""
    try:
        video_url = request.form.get('video_url', '').strip()
        
        if not video_url:
            flash('Please enter a TikTok video URL', 'error')
            return redirect(url_for('index'))
        
        # Validate TikTok URL
        if not downloader.is_valid_tiktok_url(video_url):
            flash('Please enter a valid TikTok video URL', 'error')
            return redirect(url_for('index'))
        
        # Download video
        logging.info(f"Starting download for URL: {video_url}")
        result = downloader.download_video(video_url)
        
        if result['success']:
            # Check if it's a mobile device
            user_agent = request.headers.get('User-Agent', '').lower()
            is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad'])
            
            response = send_file(
                result['file_path'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype='application/octet-stream'  # Force download instead of play
            )
            
            # Add stronger headers for mobile devices
            response.headers['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Transfer-Encoding'] = 'binary'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            if is_mobile:
                # Additional mobile-specific headers
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['Content-Description'] = 'File Transfer'
                
            return response
        else:
            flash(f'Download failed: {result["error"]}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Error in download_video: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({'status': 'healthy', 'message': 'TikTok Downloader is running'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logging.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
