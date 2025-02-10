# CoBot CLI

## Cobot API

> App Flow
> 
> Desktop or native mobile apps can use our app flow. For this, the app has to collect the email and password from the user and then exchange it for an access token.
>
>    POST https://www.cobot.me/oauth/access_token \
>    ?scope=<scopes you need, separated by spaces> \
>    &grant_type=password \
>    &username=<email of the user> \
>    &password=<password of the user> \
>    &client_id=<client id of your app> \
>    &client_secret=<client secret of your app>

OAuth2 Details for CoBot CLI

CoBot CLI

Client Id:
<YOUR_CLIENT_ID>

Client Secret:
<YOUR_CLIENT_SECRET>

Scope:
read_bookings, read_resource_categories, read_resources, read_user, and write_bookings

Redirect URL:
https://motionlabbot.tiktuk.net/callback

Authorize URL:
https://www.cobot.me/oauth/authorize

Access Token URL:
https://www.cobot.me/oauth/access_token

> Access Token
> 
> This access token is only valid for your user.
> It should be mainly used for testing and for non-interactive apps.

    <YOUR_ACCESS_TOKEN>

> To make API requests, you can either send the token as a parameter called `access_token` or as a header like this: Authorization: Bearer <your access token>.

[OAuth Flow | Cobot API](https://www.cobot.me/api-docs/oauth-flow)

Example request:

    http POST 'https://www.cobot.me/oauth/access_token?scope=read_user&grant_type=password&username=<YOUR_EMAIL>&password=<YOUR_PASSWORD>&client_id=<YOUR_CLIENT_ID>&client_secret=<YOUR_CLIENT_SECRET>'

Returns:

    {
        "access_token": "<ACCESS_TOKEN>",
        "token_type": "bearer"
    }

Showing the calendar bookings in the web interface:

    https://api.cobot.me/spaces/<SPACE_ID>/bookings?filter%5Bfrom%5D=2021-12-05T23%3A00%3A00Z&filter%5Bto%5D=2021-12-12T22%3A59%3A59Z

Example API request:

    http 'https://api.cobot.me/spaces/<SPACE_ID>/bookings?filter%5Bfrom%5D=2021-12-05T23%3A00%3A00Z&filter%5Bto%5D=2021-12-12T22%3A59%3A59Z' Authorization:'Bearer <YOUR_ACCESS_TOKEN>' Accept:application/vnd.api+json

## Running

    $ uv sync
    Resolved 17 packages in 11ms
    Audited 16 packages in 1ms
    
    $ uv pip install -e .
    Audited 1 package in 23ms
    
    $ uv run cobot <TOKEN>
