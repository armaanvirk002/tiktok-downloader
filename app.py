import os
import logging
import tempfile
import re
import threading
import time
import yt_dlp
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

class TikTokDownloader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def is_valid_tiktok_url(self, url):
        if not url:
            return False
        url = str(url).strip()
        patterns = [
            "tiktok.com/@",
            "tiktok.com/t/",
            "vm.tiktok.com/",
            "vt.tiktok.com/",
            "m.tiktok.com/v/"
        ]
        return any(pattern in url for pattern in patterns)
    
    def download_video(self, url):
        try:
            if not self.is_valid_tiktok_url(url):
                return {"success": False, "error": "Invalid TikTok URL", "filename": None}
            
            ydl_opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": os.path.join(tempfile.gettempdir(), "tiktok_video.%(ext)s"),
                "writeinfojson": False,
                "writesubtitles": False,
                "no_warnings": True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return {"success": False, "error": "Could not extract video info", "filename": None}
                
                ydl.download([url])
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    return {"success": False, "error": "File not created", "filename": None}
                
                return {
                    "success": True,
                    "filename": filename,
                    "title": info.get("title", "TikTok Video")
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "filename": None}

downloader = TikTokDownloader()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    try:
        url = request.form.get("url", "").strip()
        
        if not url:
            flash("Please enter a TikTok URL", "error")
            return redirect(url_for("index"))
        
        result = downloader.download_video(url)
        
        if not result["success"]:
            flash("Download failed: " + result["error"], "error")
            return redirect(url_for("index"))
        
        filename = result["filename"]
        
        if not os.path.exists(filename):
            flash("File not found", "error")
            return redirect(url_for("index"))
        
        return send_file(filename, as_attachment=True, download_name="tiktok_video.mp4")
        
    except Exception as e:
        flash("Error: " + str(e), "error")
        return redirect(url_for("index"))

@app.route("/validate", methods=["POST"])
def validate_url():
    try:
        data = request.get_json()
        url = data.get("url", "")
        is_valid = downloader.is_valid_tiktok_url(url)
        
        return jsonify({
            "valid": is_valid,
            "message": "Valid URL" if is_valid else "Invalid URL"
        })
        
    except Exception:
        return jsonify({"valid": False, "message": "Error"}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404

@app.errorhandler(500)
def server_error(error):
    flash("Server error", "error")
    return render_template("index.html"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
