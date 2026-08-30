# Firebase Setup Guide for CIRIS

## Quick Setup (For Development)

The backend is now configured to work with Firebase authentication. Follow these steps:

### Option 1: Using Service Account Key (Recommended)

1. **Download Service Account Key:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Select project: `ciris-493917`
   - Go to: **Project Settings** → **Service Accounts** → **Firebase Admin SDK**
   - Click **Generate new private key**
   - Save as `firebase-credentials.json` in the project root

2. **Update `.env` file:**
   ```
   FIREBASE_PROJECT_ID=ciris-493917
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   ```

3. **Restart the app:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Option 2: Environment Variables Only (Google Cloud)

If running on Google Cloud, set:
```bash
export GOOGLE_CLOUD_PROJECT=ciris-493917
```

### Option 3: Default Credentials (Local Development Alternative)

The backend will automatically use Application Default Credentials if available:
- On macOS/Linux: `~/.config/gcloud/application_default_credentials.json`
- On Windows: `%APPDATA%\gcloud\application_default_credentials.json`

## Verify Setup

When the app starts, you should see in the terminal:
```
Firebase initialized with credentials file. Project ID: ciris-493917
```

Or for default credentials:
```
Firebase initialized with default credentials. Project ID: ciris-493917
```

## Testing Authentication

1. Start the app: `uvicorn app.main:app --reload`
2. Open browser to: `http://localhost:8000/login`
3. Click **Sign in with Google** or use email/password
4. You should be redirected to dashboard after successful login

## Frontend Configuration

The frontend (login.html) uses this Firebase config:
```javascript
const firebaseConfig = {
    apiKey: "YOUR_FIREBASE_API_KEY",
    authDomain: "ciris-493917.firebaseapp.com",
    projectId: "ciris-493917",
    storageBucket: "ciris-493917.firebasestorage.app",
    messagingSenderId: "507383874363",
    appId: "1:507383874363:web:78cfbef69fd3576735ad1e"
};
```

## Troubleshooting

**Error: "A project ID is required to access the auth service"**
- Make sure `firebase-credentials.json` exists in project root OR
- Set `FIREBASE_PROJECT_ID` environment variable OR
- Set `GOOGLE_CLOUD_PROJECT` environment variable

**Error: "Firebase Admin SDK not installed"**
- Run: `pip install firebase-admin`

**Google Sign-in popup doesn't work**
- Ensure your localhost is whitelisted in Firebase Console:
  - Go to **Authentication** → **Settings** → **Authorized domains**
  - Add `localhost` if not present

## File Structure

```
ciris/
├── .env                          # Your environment variables (don't commit)
├── .env.example                  # Example .env template
├── firebase-credentials.json     # Service account key (don't commit!)
├── requirements.txt
├── app/
│   ├── main.py
│   └── templates/
│       └── login.html            # Frontend Firebase config
```

## Security Notes

⚠️ **Important:** 
- Never commit `firebase-credentials.json` to git
- Never commit `.env` file with real credentials
- Add these to `.gitignore`:
  ```
  firebase-credentials.json
  .env
  .env.local
  ```

## Environment Variables Reference

| Variable | Value | Required |
|----------|-------|----------|
| `FIREBASE_PROJECT_ID` | `ciris-493917` | Yes (or use service account) |
| `FIREBASE_CREDENTIALS_PATH` | `./firebase-credentials.json` | Optional (if using service account) |
| `GOOGLE_CLOUD_PROJECT` | `ciris-493917` | Optional (for Google Cloud) |

