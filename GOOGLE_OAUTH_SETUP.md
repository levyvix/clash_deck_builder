# Google OAuth Setup Guide

This guide walks you through setting up Google OAuth authentication for the Clash Royale Deck Builder application.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create or Select Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Either:
   - **Create a new project**: Click "Select a project" → "New Project" → Enter "Clash Royale Deck Builder" → Create
   - **Use existing project**: Select your existing project from the dropdown

## Step 2: Enable Google Identity Services API

1. In the Google Cloud Console, navigate to **APIs & Services** → **Library**
2. Search for "Google Identity Services API"
3. Click on it and press **Enable**
4. Wait for the API to be enabled (this may take a few moments)

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace account)
3. Click **Create**
4. Fill in the required information:
   - **App name**: `Clash Royale Deck Builder`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click **Save and Continue**
6. On the Scopes page, click **Save and Continue** (no additional scopes needed)
7. On the Test users page, click **Save and Continue** (you can add test users later if needed)
8. Review the summary and click **Back to Dashboard**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application** as the application type
4. Enter a name: `Clash Royale Deck Builder Web Client`
5. Configure **Authorized JavaScript origins**:
   - Click **Add URI** and enter: `http://localhost:3000`
   - Click **Add URI** and enter: `http://localhost:8000`
   - Add your production domain when ready (e.g., `https://yourdomain.com`)
6. Configure **Authorized redirect URIs**:
   - Click **Add URI** and enter: `http://localhost:3000/auth/callback`
   - Add your production callback URL when ready (e.g., `https://yourdomain.com/auth/callback`)
7. Click **Create**

## Step 5: Copy Credentials

After creating the OAuth client, you'll see a dialog with your credentials:

1. **Copy the Client ID** - it looks like: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
2. **Copy the Client Secret** - it looks like: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

## Step 6: Update Environment Variables

### Backend Configuration

Update `backend/.env`:
```bash
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

### Frontend Configuration

Update `frontend/.env`:
```bash
REACT_APP_GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
```

**Important**: Use the same Client ID for both backend and frontend!

## Step 7: Generate JWT Secret Key

For the JWT secret key, generate a secure random string. You can use:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

Update the `JWT_SECRET_KEY` in your `backend/.env` file with this generated value.

## Step 8: Verify Configuration

1. Ensure all environment variables are set correctly
2. Restart your development servers if they were running
3. The Google Sign-In button should work once the frontend implementation is complete

## Production Deployment

When deploying to production:

1. Update the OAuth credentials in Google Cloud Console:
   - Add your production domain to **Authorized JavaScript origins**
   - Add your production callback URL to **Authorized redirect URIs**
2. Update your production environment variables with the same Client ID and Client Secret
3. Use a strong, unique JWT secret key for production

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" error**: 
   - Check that your redirect URI in the code matches exactly what's configured in Google Cloud Console
   - Ensure there are no trailing slashes or typos

2. **"origin_mismatch" error**:
   - Verify that your JavaScript origins are correctly configured
   - Check that you're accessing the app from the correct URL (http://localhost:3000)

3. **Invalid Client ID**:
   - Ensure the Client ID is copied correctly without extra spaces
   - Verify the Client ID matches between frontend and backend configuration

### Getting Help

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google Cloud Console Help](https://cloud.google.com/support)

## Security Notes

- Never commit your actual Client Secret to version control
- Use environment variables for all sensitive configuration
- Regularly rotate your JWT secret key in production
- Monitor your OAuth usage in Google Cloud Console
- Consider implementing additional security measures like CSRF protection