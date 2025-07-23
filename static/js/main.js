// TikTok Downloader - Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeDownloadForm();
    initializeAnimations();
    initializeTooltips();
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

/**
 * Initialize download form functionality
 */
function initializeDownloadForm() {
    const form = document.getElementById('downloadForm');
    const urlInput = document.getElementById('videoUrl');
    const downloadBtn = document.getElementById('downloadBtn');
    
    if (!form || !urlInput || !downloadBtn) return;
    
    // Form submission handler
    form.addEventListener('submit', function(e) {
        const url = urlInput.value.trim();
        
        if (!url) {
            e.preventDefault();
            showAlert('Please enter a TikTok video URL', 'error');
            return;
        }
        
        if (!isValidTikTokUrl(url)) {
            e.preventDefault();
            showAlert('Please enter a valid TikTok video URL', 'error');
            return;
        }
        
        // Show loading state
        setLoadingState(downloadBtn, true);
        
        // For mobile devices, add special handling
        if (isMobileDevice()) {
            e.preventDefault();
            handleMobileDownload(url);
        }
        
        // Allow form to submit normally for desktop
        // Loading state will be cleared when page reloads
    });
    
    // URL input validation on paste
    urlInput.addEventListener('paste', function(e) {
        setTimeout(function() {
            const url = urlInput.value.trim();
            if (url && !isValidTikTokUrl(url)) {
                showAlert('Please enter a valid TikTok video URL', 'warning');
                urlInput.classList.add('is-invalid');
            } else {
                urlInput.classList.remove('is-invalid');
            }
        }, 100);
    });
    
    // Clear validation on input
    urlInput.addEventListener('input', function() {
        urlInput.classList.remove('is-invalid');
    });
    
    // Auto-focus on input
    urlInput.focus();
}

/**
 * Validate TikTok URL format
 * @param {string} url - URL to validate
 * @returns {boolean} - Whether URL is valid TikTok URL
 */
function isValidTikTokUrl(url) {
    const tiktokPatterns = [
        /^https?:\/\/(www\.)?tiktok\.com\/@[\w.-]+\/video\/\d+/,
        /^https?:\/\/vm\.tiktok\.com\/[\w\-]+/,
        /^https?:\/\/vt\.tiktok\.com\/[\w\-]+/,
        /^https?:\/\/m\.tiktok\.com\/v\/\d+/,
        /^https?:\/\/(www\.)?tiktok\.com\/t\/[\w\-]+/,
        /^https?:\/\/(www\.)?tiktok\.com\/@[\w.-]+\/video\/\d+\?.*/,
        /^https?:\/\/(www\.)?tiktok\.com\/[\w\-@.\/]+/
    ];
    
    // Basic check: must contain tiktok domain
    if (!url.toLowerCase().includes('tiktok.com') && !url.toLowerCase().includes('vm.tiktok.com') && !url.toLowerCase().includes('vt.tiktok.com')) {
        return false;
    }
    
    return tiktokPatterns.some(pattern => pattern.test(url));
}

/**
 * Set loading state for button
 * @param {Element} button - Button element
 * @param {boolean} loading - Whether to show loading state
 */
function setLoadingState(button, loading) {
    if (loading) {
        button.disabled = true;
        button.classList.add('btn-loading');
        button.innerHTML = '<i class="fas fa-spinner me-2"></i>Processing...';
    } else {
        button.disabled = false;
        button.classList.remove('btn-loading');
        button.innerHTML = '<i class="fas fa-download me-2"></i>Download';
    }
}

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, error, warning, info)
 */
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    const alertType = type === 'error' ? 'danger' : type;
    const iconClass = type === 'error' ? 'exclamation-triangle' : 'info-circle';
    
    alertDiv.className = `alert alert-${alertType} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${iconClass} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert before form
    const form = document.getElementById('downloadForm');
    if (form) {
        form.parentNode.insertBefore(alertDiv, form);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Initialize scroll animations
 */
function initializeAnimations() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Fade in animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .step-card, .accordion-item').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('URL copied to clipboard!', 'success');
    }).catch(function() {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('URL copied to clipboard!', 'success');
    });
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Download progress tracker (if needed for future enhancements)
 * @param {number} percent - Download percentage
 */
function updateDownloadProgress(percent) {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.textContent = Math.round(percent) + '%';
    }
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('downloadForm');
        if (form) {
            form.submit();
        }
    }
    
    // Escape to clear form
    if (e.key === 'Escape') {
        const urlInput = document.getElementById('videoUrl');
        if (urlInput && urlInput === document.activeElement) {
            urlInput.value = '';
            urlInput.blur();
        }
    }
});

/**
 * Track user interactions for analytics (if needed)
 */
function trackEvent(eventName, data = {}) {
    // This can be connected to analytics services like Google Analytics
    console.log('Event:', eventName, data);
    
    // Example: Google Analytics 4
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, data);
    }
}

/**
 * Initialize error handling
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send error reports to logging service
});

// Service Worker registration for PWA capabilities (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(function(registration) {
        //         console.log('SW registered: ', registration);
        //     })
        //     .catch(function(registrationError) {
        //         console.log('SW registration failed: ', registrationError);
        //     });
    });
}

/**
 * Check if device is mobile
 */
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Handle mobile download with special headers
 */
function handleMobileDownload(url) {
    const formData = new FormData();
    formData.append('video_url', url);
    
    fetch('/download', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Download failed');
    })
    .then(blob => {
        // Create download link for mobile
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = `tiktok_video_${Date.now()}.mp4`;
        
        // Add to DOM, click, then remove
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        }, 100);
        
        setLoadingState(document.getElementById('downloadBtn'), false);
        showAlert('Download started! Check your downloads folder.', 'success');
    })
    .catch(error => {
        console.error('Download error:', error);
        setLoadingState(document.getElementById('downloadBtn'), false);
        showAlert('Download failed. Please try again.', 'error');
    });
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isValidTikTokUrl,
        formatFileSize,
        copyToClipboard,
        isMobileDevice
    };
}
