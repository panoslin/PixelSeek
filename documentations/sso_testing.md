# SSO Authentication Testing Guide for PixelSeek

This guide explains how to test the SSO authentication system in a local development environment.

## Prerequisites

1. Running MongoDB instance
2. Running Django backend
3. Running React frontend
4. Test OAuth credentials for Google/WeChat

## Setting Up Test Credentials

### Google OAuth Testing

1. Create test credentials in the [Google Cloud Console](https://console.cloud.google.com/):
   - Create a new project (or use an existing one)
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Set application type as "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/api/users/auth/google/callback`
   - Note your Client ID and Client Secret

2. Update your `.env` file with test credentials:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your-test-client-id
   GOOGLE_OAUTH_SECRET=your-test-client-secret
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/users/auth/google/callback
   ```

### WeChat OAuth Testing

Option 1: Using test credentials from WeChat Developer Platform:
1. Register a developer account at [WeChat Developer Platform](https://open.weixin.qq.com/)
2. Create a test app and obtain test credentials
3. Configure your `.env` file:
   ```
   WECHAT_OAUTH_APP_ID=your-test-app-id
   WECHAT_OAUTH_SECRET=your-test-secret
   WECHAT_OAUTH_REDIRECT_URI=http://localhost:8000/api/users/auth/wechat/callback
   ```

Option 2: Using mock WeChat server for local testing:
1. Set up a mock OAuth server (described in the next section)
2. Configure your `.env` file to point to the mock server

## Setting Up a Mock OAuth Server for Local Testing

If you don't want to use real OAuth providers during development, you can use a mock OAuth server.

### Installing the Mock Server

```bash
npm install -g mockoon
```

### Running the Mock OAuth Server

1. Start Mockoon and create a new environment
2. Add these endpoints:

#### Google Mock Endpoints:
- `GET /o/oauth2/auth` - Redirects to a mock login page
- `POST /oauth2/token` - Returns mock tokens
- `GET /userinfo` - Returns mock user info

#### WeChat Mock Endpoints:
- `GET /connect/qrconnect` - Redirects to a mock login page 
- `GET /sns/oauth2/access_token` - Returns mock access token
- `GET /sns/userinfo` - Returns mock user info

### Mock Response Example for Google Token:

```json
{
  "access_token": "mock-access-token",
  "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlfQ.mock-signature",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Mock Response Example for WeChat Token:

```json
{
  "access_token": "mock-wechat-access-token",
  "openid": "mock-openid-12345",
  "expires_in": 7200
}
```

### Mock Response Example for WeChat User Info:

```json
{
  "openid": "mock-openid-12345",
  "nickname": "TestWeChatUser",
  "sex": 1,
  "city": "Shanghai",
  "province": "Shanghai",
  "country": "CN",
  "headimgurl": "https://thispersondoesnotexist.com/image"
}
```

## Testing the SSO Flow

1. Start your Django backend:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Start your React frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Navigate to `http://localhost:3000/login` in your browser

4. Click on "Sign in with Google" or "Sign in with WeChat"

5. If using real credentials, you'll be redirected to the actual provider login page
   - Use a test account to login

6. If using mock server, you'll be redirected to the mock login page
   - Enter any credentials to proceed

7. After successful authentication, you should be redirected back to your application
   - The frontend will receive JWT tokens
   - You should be redirected to the dashboard

## Troubleshooting

### Common Issues:

1. **Redirect URI Mismatch**:
   - Ensure that the redirect URI in Google/WeChat console exactly matches the one in your `.env` file
   - Check for trailing slashes

2. **CORS Issues**:
   - Verify that your Django backend has CORS properly configured
   - Check that the frontend origin is in the allowed origins list

3. **Token Validation Issues**:
   - Check the browser console for any errors during token processing
   - Verify that the JWT tokens are correctly formatted

4. **MongoDB Connection**:
   - Ensure MongoDB is running and accessible
   - Check that the connection string in `.env` is correct

## Using the Authentication API Directly

You can also test the authentication API directly using tools like Postman or curl:

### JWT Token Generation:

```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpassword"}'
```

### JWT Token Refresh:

```bash
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your-refresh-token"}'
```

### Getting User Profile:

```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer your-access-token"
```

## Security Considerations for Production

1. **Always use HTTPS** in production
2. **Store tokens securely**:
   - Use HttpOnly cookies for JWT storage in production
   - Consider implementing token rotation
3. **Set appropriate token expiration times**
4. **Implement rate limiting** on token endpoints
5. **Monitor for suspicious authentication attempts** 