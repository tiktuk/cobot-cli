# CoBot CLI

A command-line interface for interacting with the Cobot API.

## Authentication

The CoBot CLI uses OAuth2 for authentication with the Cobot API. There are two authentication methods available:

### 1. App Flow (For Development)

For development and testing, you can use the password grant flow:

```bash
POST https://www.cobot.me/oauth/access_token
    ?scope=<scopes>
    &grant_type=password
    &username=<email>
    &password=<password>
    &client_id=<client_id>
    &client_secret=<client_secret>
```

### 2. OAuth2 Configuration

For production use, the CLI is configured with the following OAuth2 details:

- **Client ID**: `<YOUR_CLIENT_ID>`
- **Client Secret**: `<YOUR_CLIENT_SECRET>`
- **Scopes**: read_bookings, read_resource_categories, read_resources, read_user, write_bookings
- **Redirect URL**: https://motionlabbot.tiktuk.net/callback
- **Authorize URL**: https://www.cobot.me/oauth/authorize
- **Access Token URL**: https://www.cobot.me/oauth/access_token

The access token obtained is user-specific and should be handled securely.

## API Usage

### Making API Requests

You can include the access token in requests either:
- As a query parameter: `?access_token=<token>`
- As a header: `Authorization: Bearer <token>`

### Example Requests

1. **Getting an Access Token**:
```bash
http POST 'https://www.cobot.me/oauth/access_token' \
    scope='read_user' \
    grant_type='password' \
    username='<YOUR_EMAIL>' \
    password='<YOUR_PASSWORD>' \
    client_id='<YOUR_CLIENT_ID>' \
    client_secret='<YOUR_CLIENT_SECRET>'
```

Response:
```json
{
    "access_token": "<ACCESS_TOKEN>",
    "token_type": "bearer"
}
```

2. **Fetching Calendar Bookings**:
```bash
http 'https://api.cobot.me/spaces/<SPACE_ID>/bookings' \
    filter[from]='2021-12-05T23:00:00Z' \
    filter[to]='2021-12-12T22:59:59Z' \
    Authorization:'Bearer <YOUR_ACCESS_TOKEN>' \
    Accept:'application/vnd.api+json'
```

## Installation and Usage

1. Install dependencies:
```bash
uv sync
```

2. Install the CLI in development mode:
```bash
uv pip install -e .
```

3. Run the CLI:
```bash
uv run cobot <TOKEN>
```

For more information about the OAuth flow, visit the [Cobot API Documentation](https://www.cobot.me/api-docs/oauth-flow).
