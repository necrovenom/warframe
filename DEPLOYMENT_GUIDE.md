# Vercel Deployment Guide

## Files needed for Vercel deployment:

1. **vercel.json** - Vercel configuration (✓ already created)
2. **api/index.py** - Main Flask app as serverless function (✓ already created)
3. **templates/** - HTML templates directory (✓ already exists)
4. **app.py** - Your Warframe data processing logic (✓ already exists)

## Steps to deploy on Vercel:

1. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Import your repository

2. **Deployment settings:**
   - Framework: Other
   - Build command: (leave empty)
   - Output directory: (leave empty)
   - Install command: `pip install flask requests`

3. **Environment variables** (if needed):
   - Add any API keys as environment variables in Vercel dashboard

## Key differences from Replit:

- **Serverless functions**: Vercel runs each request as a separate function
- **Cold starts**: First request may be slower as data loads
- **File structure**: API endpoints must be in `/api/` directory
- **Dependencies**: Uses requirements.txt for Python packages

## Common issues and solutions:

1. **Import errors**: Fixed by adding parent directory to sys.path
2. **Template not found**: Fixed by setting template_folder='../templates'
3. **Data loading**: Added init_data() function to load data on demand
4. **Serverless timeouts**: Large data may need optimization for faster loading

## Current status:
✓ Flask app restructured for Vercel serverless
✓ Templates and static files properly referenced
✓ Error handling for missing dependencies
✓ Fallback imports if app.py modules fail