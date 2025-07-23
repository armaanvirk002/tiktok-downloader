import os
import tempfile
import logging
import re
from urllib.parse import urlparse
import yt_dlp
from typing import Dict, Any, Optional

class TikTokDownloader:
    """TikTok video downloader using yt-dlp"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # yt-dlp configuration for TikTok
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer mp4 format
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
        """
        Validate if the URL is a valid TikTok video URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid TikTok URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Basic check: must contain tiktok domain
        url_lower = url.strip().lower()
        if not ('tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower or 'vt.tiktok.com' in url_lower):
            return False
        
        # TikTok URL patterns - more permissive
        tiktok_patterns = [
            r'^https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'^https?://vm\.tiktok\.com/[\w\-]+',
            r'^https?://vt\.tiktok\.com/[\w\-]+',
            r'^https?://m\.tiktok\.com/v/\d+',
            r'^https?://(www\.)?tiktok\.com/t/[\w\-]+',
            r'^https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+\?.*',
            r'^https?://(www\.)?tiktok\.com/[\w\-@.\/]+',
        ]
        
        for pattern in tiktok_patterns:
            if re.match(pattern, url.strip()):
                return True
        
        return False
    
    def extract_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract video information without downloading
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Video information or None if failed
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    return None
                return {
                    'title': info.get('title', 'TikTok Video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'id': info.get('id', ''),
                    'ext': info.get('ext', 'mp4'),
                    'filesize': info.get('filesize', 0),
                }
        except Exception as e:
            self.logger.error(f"Error extracting video info: {str(e)}")
            return None
    
    def download_video(self, url: str) -> Dict[str, Any]:
        """
        Download TikTok video without watermark
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Download result with success status, file path, and error message
        """
        try:
            # Validate URL
            if not self.is_valid_tiktok_url(url):
                return {
                    'success': False,
                    'error': 'Invalid TikTok URL format',
                    'file_path': None,
                    'filename': None
                }
            
            self.logger.info(f"Starting download for URL: {url}")
            
            # Create temporary directory for downloads
            temp_dir = tempfile.gettempdir()
            
            # Update output template with temporary directory
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = os.path.join(temp_dir, 'tiktok_%(id)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Extract video info first
                info = ydl.extract_info(url, download=False)
                if not info:
                    return {
                        'success': False,
                        'error': 'Could not extract video information',
                        'file_path': None,
                        'filename': None
                    }
                
                # Generate filename
                video_id = info.get('id', 'unknown')
                ext = info.get('ext', 'mp4')
                filename = f"tiktok_{video_id}.{ext}"
                file_path = os.path.join(temp_dir, filename)
                
                # Check if file already exists
                if os.path.exists(file_path):
                    self.logger.info(f"File already exists: {filename}")
                    return {
                        'success': True,
                        'file_path': file_path,
                        'filename': filename,
                        'video_info': {
                            'title': info.get('title', 'TikTok Video'),
                            'uploader': info.get('uploader', 'Unknown'),
                            'duration': info.get('duration', 0),
                        }
                    }
                
                # Download the video
                ydl.download([url])
                
                # Verify file was created
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    self.logger.info(f"Download successful: {filename} ({file_size} bytes)")
                    
                    return {
                        'success': True,
                        'file_path': file_path,
                        'filename': filename,
                        'file_size': file_size,
                        'video_info': {
                            'title': info.get('title', 'TikTok Video'),
                            'uploader': info.get('uploader', 'Unknown'),
                            'duration': info.get('duration', 0),
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Video file was not created',
                        'file_path': None,
                        'filename': None
                    }
                    
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            self.logger.error(f"yt-dlp download error: {error_msg}")
            
            # Provide user-friendly error messages
            if "Video unavailable" in error_msg:
                error_msg = "Video is unavailable or has been removed"
            elif "Private video" in error_msg:
                error_msg = "This is a private video and cannot be downloaded"
            elif "Sign in to confirm your age" in error_msg:
                error_msg = "Age-restricted video cannot be downloaded"
            elif "HTTP Error 403" in error_msg:
                error_msg = "Access denied. The video may be region-restricted"
            elif "HTTP Error 404" in error_msg:
                error_msg = "Video not found. Please check the URL"
            else:
                error_msg = "Failed to download video. Please try again"
            
            return {
                'success': False,
                'error': error_msg,
                'file_path': None,
                'filename': None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error during download: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred. Please try again',
                'file_path': None,
                'filename': None
            }
    
    def get_supported_sites(self) -> list:
        """
        Get list of supported sites by yt-dlp
        
        Returns:
            list: List of supported site names
        """
        try:
            # Return known TikTok-related extractors
            return ['TikTok', 'TikTokUser', 'TikTokVM']
        except Exception as e:
            self.logger.error(f"Error getting supported sites: {str(e)}")
            return ['TikTok']
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """
        Clean up old downloaded files
        
        Args:
            max_age_hours (int): Maximum age of files in hours before cleanup
        """
        try:
            import time
            temp_dir = tempfile.gettempdir()
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(temp_dir):
                if filename.startswith('tiktok_'):
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.isfile(filepath):
                        file_age = current_time - os.path.getmtime(filepath)
                        if file_age > max_age_seconds:
                            os.remove(filepath)
                            self.logger.info(f"Cleaned up old file: {filename}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
