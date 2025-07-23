import os
import logging
import tempfile
import re
import threading
import time
from urllib.parse import urlparse
from typing import Dict, Any, Optional
import yt_dlp
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TikTokDownloader:
    """TikTok video downloader using yt-dlp"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # yt-dlp configuration for TikTok
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(tempfile.gettempdir(), 'tiktok_%(id)s.%(ext)s'),
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'no_warnings': False,
            'extractflat': False,
            'writethumbnail': False,
            'extract_flat': False,
            'cookiefile': None,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        }
    
    def is_valid_tiktok_url(self, url: str) -> bool:
        """Validate if the URL is a valid TikTok video URL"""
        if not url or not isinstance(url, str):
            return False
        
        tiktok_patterns = [
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://(?:www\.)?tiktok\.com/t/\w+',
            r'https?://vm\.tiktok\.com/\w+',
            r'https?://vt\.tiktok\.com/\w+',
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+\?.*',
            r'https?://m\.tiktok\.com/v/\d+\.html',
        ]
        
        return any(re.match(pattern, url.strip()) for pattern in tiktok_patterns)
    
    def download_video(self, url: str) -> Dict[str, Any]:
        """Download TikTok video and return file information"""
        try:
            if not self.is_valid_tiktok_url(url):
                return {
                    'success': False,
                    'error': 'Invalid TikTok URL format',
                    'filename': None
                }
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {
                        'success': False,
                        'error': 'Could not extract video information',
                        'filename': None
                    }
                
                ydl.download([url])
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    return {
                        'success': False,
                        'error': 'Video file was not created',
                        'filename': None
                    }
                
                return {
                    'success': True,
                    'filename': filename,
                    'title': info.get('title', 'TikTok Video'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count')
                }
                
        except Exception as e:
            self.logger.error(f"Error downloading TikTok video: {str(e)}")
            return {
                'success': False,
                'error': f'Download failed: {str(e)}',
                'filename': None
            }

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize TikTok downloader
downloader = TikTokDownloader()

# File cleanup configuration
CLEANUP_INTERVAL = 3600  # 1 hour in seconds
MAX_FILE_AGE = 3600      # 1 hour in seconds

def cleanup_old_files():
    """Background task to clean up old downloaded files"""
    while True:
        try:
            temp_dir = tempfile.gettempdir()
            current_time = time.time()
            
            for filename in os.listdir(temp_dir):
                if filename.startswith('tiktok_') and filename.endswith('.mp4'):
                    file_path = os.path.join(temp_dir, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > MAX_FILE_AGE:
                            try:
                                os.remove(file_path)
                                app.logger.info(f"Cleaned up old file: {filename}")
                            except OSError as e:
                                app.logger.error(f"Error removing file {filename}: {e}")
            
        except Exception as e:
            app.logger.error(f"Error in cleanup task: {e}")
        
        time.sleep(CLEANUP_INTERVAL)

# Start cleanup task in background
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    """Handle video download request"""
    try:
        url = request.form.get('url', '').strip()
        
        if not url:
            flash('Please enter a TikTok video URL', 'error')
            return redirect(url_for('index'))
        
        app.logger.info(f"Download request for URL: {url}")
        
        # Download the video
        result = downloader.download_video(url)
        
        if not result['success']:
            flash(f"Download failed: {result['error']}", 'error')
            return redirect(url_for('index'))
        
        filename = result['filename']
        
        if not os.path.exists(filename):
            flash('Downloaded file not found', 'error')
            return redirect(url_for('index'))
        
        # Generate a safe filename for download
        title = result.get('title', 'TikTok Video')
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        download_filename = f"{safe_title}.mp4"
        
        app.logger.info(f"Sending file: {filename} as {download_filename}")
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=download_filename,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        app.logger.error(f"Error in download route: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/validate', methods=['POST'])
def validate_url():
    """Validate TikTok URL via AJAX"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        is_valid = downloader.is_valid_tiktok_url(url)
        
        return jsonify({
            'valid': is_valid,
            'message': 'Valid TikTok URL' if is_valid else 'Please enter a valid TikTok video URL'
        })
        
    except Exception as e:
        app.logger.error(f"Error in validate route: {str(e)}")
        return jsonify({
            'valid': False,
            'message': 'Error validating URL'
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {error}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
