# 🚀 Deployment Guide with Password Protection

Your Stay vs. Go app now includes password protection. Follow these steps to deploy securely.

## 🔒 Password Setup (Before Deployment)

### Default Password
- **Current password**: `horowitz2026`
- **Where it's stored**: `.streamlit/secrets.toml`

### Change the Password (Recommended)

**For local testing:**
1. Edit `.streamlit/secrets.toml`
2. Change `password = "horowitz2026"` to your preferred password
3. Restart the app

**For production deployment:**
- See "Step 3: Configure Secrets" below (Streamlit Cloud manages this securely)

---

## 📦 Deploy to Streamlit Cloud (Free)

### Step 1: Push to GitHub

```bash
# Initialize git repository
git init

# Add all files (except secrets - already in .gitignore)
git add .

# Commit
git commit -m "Initial deployment of Stay vs Go tool"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/stay-vs-go.git
git branch -M main
git push -u origin main
```

**IMPORTANT**: The `.gitignore` file ensures `.streamlit/secrets.toml` is NOT pushed to GitHub. Your password stays private.

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `yourusername/stay-vs-go`
   - **Branch**: `main`
   - **Main file path**: `stay_vs_go_app.py`
5. Click **"Deploy"**

### Step 3: Configure Secrets (Password)

Before your app is fully functional, you need to add the password to Streamlit Cloud:

1. In your app dashboard on Streamlit Cloud, click **"Settings"** (⚙️ icon)
2. Click **"Secrets"** in the left sidebar
3. Paste this into the secrets editor:
   ```toml
   password = "your_secure_password_here"
   ```
4. Replace `your_secure_password_here` with your actual client password
5. Click **"Save"**
6. Your app will automatically restart

### Step 4: Share with Clients

Your app will be live at: `https://your-app-name.streamlit.app`

**To share with clients:**
- Send them the URL
- Send them the password separately (email, text, etc.)
- They'll see a password prompt on first visit

---

## 🔐 Security Best Practices

### Use Strong Passwords
```toml
# Bad
password = "12345"

# Better
password = "StayVsGo2026!"

# Best (for sensitive clients)
password = "T7$mK9@pL2&vN4"
```

### Multiple Passwords (Advanced)
For different client tiers, you can modify the code to check multiple passwords:

```python
# In stay_vs_go_app.py, replace the check_password function
def check_password():
    def password_entered():
        allowed_passwords = [
            st.secrets.get("password", "horowitz2026"),
            st.secrets.get("password_tier2", ""),
            st.secrets.get("password_admin", "")
        ]
        if st.session_state["password"] in allowed_passwords and st.session_state["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    # ... rest of function
```

Then in Streamlit Cloud secrets:
```toml
password = "client_password"
password_tier2 = "premium_client_password"
password_admin = "admin_only_password"
```

---

## 🧪 Testing Locally

Before deploying, test the password protection:

```bash
# Run the app
streamlit run stay_vs_go_app.py

# Try these scenarios:
# 1. Enter wrong password → should show error
# 2. Enter correct password → should load app
# 3. Refresh page → should stay logged in (session state)
```

---

## 🔄 Updating the App

After initial deployment, updates are automatic:

```bash
# Make your changes to stay_vs_go_app.py
git add .
git commit -m "Updated calculation logic"
git push

# Streamlit Cloud automatically redeploys!
# Your clients will see changes within 1-2 minutes
```

---

## 🆘 Troubleshooting

### "Password incorrect" even with right password
- **Cause**: Secret not configured on Streamlit Cloud
- **Fix**: Go to app Settings → Secrets, verify password is set correctly

### Password prompt not showing
- **Cause**: Code error before password check
- **Fix**: Check Streamlit Cloud logs (Settings → Logs)

### Want to disable password temporarily?
Comment out the password check:

```python
# if not check_password():
#     st.stop()
```

Commit and push. Re-enable when ready.

---

## 🌐 Alternative: Custom Domain

Want `stayvsgo.horowitzcommercial.com` instead of `.streamlit.app`?

1. Upgrade to Streamlit Cloud Team plan ($250/month)
2. Or deploy to Heroku/AWS with custom domain (see README.md)

---

## 📧 Client Instructions Template

Use this email template when sharing with clients:

```
Subject: Your Custom Stay vs. Go Analysis Tool

Hi [Client Name],

I've created a custom financial analysis tool for your lease decision.

Access the tool here:
https://stay-vs-go.streamlit.app

Password: [insert password]

How to use:
1. Enter the URL and password
2. Input your current lease terms in "Scenario A"
3. Input the alternative offer in "Scenario B"
4. Adjust your company details (headcount, etc.)
5. Review the breakeven analysis and 10-year projections

The tool updates in real-time as you adjust the numbers. Feel free to
experiment with different scenarios.

Questions? Let's schedule a call to walk through it together.

Best,
Sam Horowitz
[Your Contact Info]
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Run locally | `streamlit run stay_vs_go_app.py` |
| Change password (local) | Edit `.streamlit/secrets.toml` |
| Change password (cloud) | Streamlit Cloud → Settings → Secrets |
| Update app | `git push` (auto-deploys) |
| View logs | Streamlit Cloud → Settings → Logs |
| Share app | Send URL + password separately |

---

**Ready to deploy?** Push to GitHub, deploy to Streamlit Cloud, configure your password, and you're live! 🚀
