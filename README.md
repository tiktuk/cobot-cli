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
space_subdomain = "your-space-subdomain"  # Required: Your space subdomain (e.g., 'co-up' for co-up.cobot.me)
api_base = "https://api.cobot.me"  # Optional: API base URL
access_token = "your-cobot-access-token"  # Your Cobot API access token
data_dir = "~/.local/share/cobot"  # Optional: Directory for storing booking history
log_file = "logs/cobot.log"  # Optional: Log file path (relative to data_dir)

# Telegram notifications (optional)
telegram_bot_token = "your-telegram-bot-token"  # Your Telegram bot token
telegram_chat_id = "your-telegram-chat-id"  # Your Telegram chat ID
```

You can also use environment variables with the `COBOT_` prefix:

```bash
export COBOT_SPACE_ID="your-cobot-space-id"
export COBOT_SPACE_SUBDOMAIN="your-space-subdomain"
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

List your own upcoming bookings:
```bash
cobot my-bookings
```

Show weekly schedule for a resource:
```bash
cobot show-weekly-schedule RESOURCE_ID
```

Show weekly schedule with a specific token:
```bash
cobot show-weekly-schedule --token YOUR_API_TOKEN RESOURCE_ID
```
Monitor bookings for changes:
```bash
cobot monitor-bookings
```

Monitor specific resource for changes:
```bash
cobot monitor-bookings --resource RESOURCE_ID
```

Monitor with custom time range:
```bash
cobot monitor-bookings --days 14
```

The monitor command will:
- Save booking data to a JSONL file in the configured data directory
- Compare with previous state to detect cancellations and new bookings
- Show changes in a color-coded table (red for cancellations, green for new bookings)
- Send Telegram notifications for booking changes (if configured)
- Keep a complete history of all booking states for future reference

### Telegram Notifications

When Telegram is configured (using `telegram_bot_token` and `telegram_chat_id` in settings), the monitor command will automatically send notifications for:
- New bookings (✓)
- Cancelled bookings (❌)
- Error conditions (e.g., API failures)

Notifications are formatted with HTML and include:
- Date and time of the booking
- Name of the person booking
- Title/purpose of the booking

Options:
- `--days` / `-d`: Number of days to fetch bookings for (default: 7)
- `--resource` / `-r`: Filter bookings by resource ID
- `--token`: Use a specific API token (overrides settings)

## Data Storage

Booking history is stored in JSONL (JSON Lines) format in the configured data directory. Each resource's bookings are stored in a separate file named `bookings_<resource_id>.jsonl`. Each line contains a complete snapshot of bookings at a specific time, including:

- Timestamp of the snapshot
- Space ID
- Resource ID
- Complete booking data

This allows for:
- Easy tracking of booking changes over time
- Simple append-only storage
- Human-readable format
- No database setup required

The data directory can be configured in settings.toml using the `data_dir` option. The default location is `~/.local/share/cobot`.

## Logging

The CLI logs all booking changes (new bookings and cancellations) to help track and audit changes over time. Logs include:
- Timestamps for all events
- Details of cancelled bookings
- Details of new bookings
- Booking information including names, titles, and times

The log file location can be configured in settings.toml using the `log_file` option. By default, logs are stored in `~/.local/share/cobot/logs/cobot.log`. The path is relative to the configured `data_dir`.

Example log entries:
```
2024-02-11 00:03:44,123 - INFO - New booking: John Doe - Team Meeting at 2024-02-12T09:00:00Z to 2024-02-12T10:00:00Z
2024-02-11 00:03:44,124 - INFO - Cancelled booking: Jane Smith - Workshop at 2024-02-13T14:00:00Z to 2024-02-13T16:00:00Z
```

- `--resource` / `-r`: Filter bookings by resource ID
