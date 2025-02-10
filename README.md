# Cobot CLI

A command-line interface for fetching Cobot bookings.

## Configuration

The CLI can be configured using configuration files in the following locations (in order of precedence):

1. `./settings.toml` (local project directory)
2. `~/.config/cobot/settings.toml` (user-specific)
3. `/etc/cobot/settings.toml` (system-wide)

Example configuration file:

```toml
# Default settings
space_id = "your-cobot-space-id"  # Required: Your Cobot space ID
api_base = "https://api.cobot.me"  # Optional: API base URL

[development]
# Development environment specific settings
api_base = "https://api.cobot.me"

[production]
# Production environment specific settings
api_base = "https://api.cobot.me"
```

You can also use environment variables with the `COBOT_` prefix:

```bash
export COBOT_SPACE_ID="your-cobot-space-id"
export COBOT_API_BASE="https://api.cobot.me"
```

## Usage

Get bookings for the next 7 days:
```bash
cobot get-bookings
```

Get bookings with a specific token (overrides settings):
```bash
cobot get-bookings --token YOUR_API_TOKEN
```

Get bookings for a specific resource:
```bash
cobot get-bookings --resource RESOURCE_ID
```

Show weekly schedule for a resource:
```bash
cobot show-weekly-schedule RESOURCE_ID
```

Show weekly schedule with a specific token:
```bash
cobot show-weekly-schedule --token YOUR_API_TOKEN RESOURCE_ID
```

Options:
- `--days` / `-d`: Number of days to fetch bookings for (default: 7)
- `--resource` / `-r`: Filter bookings by resource ID
