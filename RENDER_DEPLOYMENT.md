# Render Deployment Guide for TikTok Downloader

## 🚀 Deploy to Render (Free & Easy)

### Step 1: Prepare Your Files
Your project is already configured for Render deployment with these files:
- ✅ `requirements.txt` - Python dependencies
- ✅ `main.py` - Application entry point
- ✅ `app.py` - Flask application
- ✅ `render.yaml` - Render configuration
- ✅ `gunicorn.conf.py` - Production server settings

### Step 2: Upload to GitHub

1. **Create a new repository on GitHub:**
   - Go to [github.com](https://github.com) and sign in
   - Click the "+" icon → "New repository"
   - Name: `tiktok-downloader` (or your choice)
   - Make it Public or Private
   - **Don't** initialize with README (we already have files)
   - Click "Create repository"

2. **Upload your files:**
   - In your new repository, click "uploading an existing file"
   - Drag and drop ALL project files from your computer
   - Commit message: `Initial commit: TikTok video downloader`
   - Click "Commit changes"

### Step 3: Deploy on Render

1. **Sign up for Render:**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account (free)

2. **Create Web Service:**
   - Click **"New +"** → **"Web Service"**
   - Click **"Connect account"** to connect GitHub
   - Select your `tiktok-downloader` repository

3. **Configure Settings:**
   Use these **exact settings**:

   **Basic Settings:**
   - **Name**: `tiktok-downloader` (or your choice)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or `master`)

   **Build & Deploy:**
   - **Root Directory**: Leave blank
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`

   **Advanced Settings:**
   - **Instance Type**: `Free` (or paid for better performance)
   - **Auto-Deploy**: `Yes` (deploys on GitHub pushes)

4. **Environment Variables (Optional):**
   Render automatically sets:
   - `PORT` - Automatically configured
   - `SESSION_SECRET` - Auto-generated for security

### Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build and deployment
3. Your app will be live at: `https://your-app-name.onrender.com`

## 📱 What You Get

Your deployed TikTok downloader includes:
- **Mobile-optimized interface** - Large inputs, touch-friendly
- **Production-ready server** - Gunicorn with proper configuration
- **All TikTok URL formats** - vm.tiktok.com, vt.tiktok.com, etc.
- **Automatic cleanup** - Removes downloaded files after use
- **Free HTTPS** - Secure connection included

## 🔧 Troubleshooting

### Build Failed?
- ✅ Check that `requirements.txt` is in root directory
- ✅ Verify build command: `pip install -r requirements.txt`
- ✅ Ensure Python version compatibility

### App Won't Start?
- ✅ Verify start command: `gunicorn --bind 0.0.0.0:$PORT main:app`
- ✅ Check that `main.py` exists and imports `app`
- ✅ Review logs in Render dashboard

### Downloads Not Working?
- ✅ This is normal on free hosting - videos download to user's device
- ✅ Mobile downloads work with our optimized headers
- ✅ Check application logs for specific errors

## 📊 Performance Expectations

**Free Tier:**
- Perfect for testing and light usage
- Sleeps after 15 minutes of inactivity
- 750 hours/month free
- Wakes up in ~30 seconds when accessed

**Paid Tiers ($7+/month):**
- Always-on hosting
- Better performance
- Custom domains available
- No sleep mode

## 🎯 Post-Deployment Checklist

After deployment, test these features:
1. ✅ Website loads on mobile and desktop
2. ✅ Large input box works on mobile devices
3. ✅ URL validation works for all TikTok formats
4. ✅ Videos download (not play) on mobile
5. ✅ No errors in Render logs

## 🔄 Updates & Maintenance

**Automatic Updates:**
- Push changes to GitHub
- Render automatically rebuilds and deploys
- No manual intervention needed

**Manual Redeploy:**
- Go to Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"

## 🌍 Custom Domain (Optional)

To use your own domain:
1. Upgrade to a paid plan
2. Go to Settings → Custom Domains
3. Add your domain and configure DNS
4. Render provides SSL certificate automatically

## 🆘 Support

If you encounter issues:
1. **Check Render logs** in the dashboard
2. **Verify all files** uploaded correctly to GitHub
3. **Ensure settings match** exactly as shown above
4. **Contact Render support** for platform issues

---

**Deployment Time:** ~5-10 minutes  
**Cost:** Free tier available  
**Scaling:** Automatic with paid plans  
**SSL:** Included automatically  

Your TikTok downloader is now ready for thousands of users! 🎉