# SEO Tools Flask App (devsites.lol ready)

## 📦 Deployment on Namecheap Shared Hosting
- Place files in `/home/abneckuv/public_html/devsites.lol/`
- Ensure Python app is created via cPanel
- Activate your virtualenv:
```bash
source /home/abneckuv/virtualenv/public_html/devsites.lol/3.11/bin/activate
pip install -r requirements.txt
```

- Restart app from cPanel

## 🔐 Default Routes:
- `/tools/meta-tag-extractor`
- `/users/login`
- `/users/register`
- `/admin/` (requires login)
