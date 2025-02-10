#!/usr/bin/env python3
import typer
import requests
from datetime import datetime, timedelta
from typing import Optional
from rich.console import Console
from rich.table import Table
from dateutil import parser
from dateutil.tz import tzutc
from .settings import settings

app = typer.Typer()
console = Console()


def fetch_bookings(
    token: Optional[str] = None,
    from_date: datetime = datetime.now(tzutc()),
    to_date: datetime = datetime.now(tzutc()) + timedelta(days=7),
    resource_id: Optional[str] = None,
) -> list:
    """Fetch bookings from Cobot API."""
    headers = {
        "Authorization": f"Bearer {token or settings.access_token}",
        "Accept": "application/vnd.api+json",
    }
    params = {
        "filter[from]": from_date.isoformat(),
        "filter[to]": to_date.isoformat(),
    }

    url = f"{settings.api_base}/spaces/{settings.space_id}/bookings"

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    bookings = response.json()["data"]

    if resource_id:
        bookings = [
            b
            for b in bookings
            if b["relationships"]["resource"]["data"]["id"] == resource_id
        ]

    return bookings


def create_bookings_table(bookings: list) -> Table:
    """Create a rich table for bookings."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date")
    table.add_column("Time")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Resource ID")

    for booking in bookings:
        attrs = booking["attributes"]
        from_time = parser.parse(attrs["from"])
        to_time = parser.parse(attrs["to"])

        # Format date and time
        date = from_time.strftime("%Y-%m-%d")
        time = f"{from_time.strftime('%H:%M')} - {to_time.strftime('%H:%M')}"

        name = attrs["name"] or "N/A"
        title = attrs["title"] or "N/A"
        resource_id = booking["relationships"]["resource"]["data"]["id"]

        table.add_row(date, time, name, title, resource_id)

    return table


@app.command()
def get_bookings(
    token: Optional[str] = typer.Option(
        None, help="Cobot API access token (overrides settings)"
    ),
    resource_id: Optional[str] = typer.Option(
        None,
        "--resource",
        "-r",
        help="Specific resource ID to filter (uses default from settings if not specified)",
    ),
    days: int = typer.Option(
        7, "--days", "-d", help="Number of days to fetch bookings for"
    ),
):
    """Fetch and display bookings from your coworking space."""
    try:
        now = datetime.now(tzutc())
        from_date = now
        to_date = now + timedelta(days=days)

        with console.status("Fetching bookings..."):
            used_resource_id = (
                resource_id or str(settings.default_resource_id)
                if settings.default_resource_id
                else None
            )
            bookings = fetch_bookings(token, from_date, to_date, used_resource_id)

        if not bookings:
            console.print(
                "No bookings found for the specified criteria.", style="yellow"
            )
            return

        table = create_bookings_table(bookings)
        console.print(table)

    except requests.exceptions.HTTPError as e:
        console.print(f"Error: Failed to fetch bookings. {str(e)}", style="red")
    except Exception as e:
        console.print(f"Error: {str(e)}", style="red")


def create_weekly_table(bookings: list, from_date: datetime, days: int) -> Table:
    """Create a rich table with days as columns and hourly time slots as rows."""
    table = Table(show_header=True, header_style="bold magenta")

    # Add columns for time and each day
    table.add_column("Time")
    for i in range(days):
        current_date = from_date + timedelta(days=i)
        table.add_column(current_date.strftime("%a %d %b"))  # Mon 10 Feb

    # Group bookings by day and time
    daily_bookings = {i: [] for i in range(days)}
    for booking in bookings:
        attrs = booking["attributes"]
        from_time = parser.parse(attrs["from"])
        days_diff = (from_time.date() - from_date.date()).days
        if 0 <= days_diff < days:
            daily_bookings[days_diff].append(booking)

    # Find earliest and latest times from bookings
    start_hours = []
    end_hours = []
    for day_bookings in daily_bookings.values():
        for booking in day_bookings:
            attrs = booking["attributes"]
            from_time = parser.parse(attrs["from"])
            to_time = parser.parse(attrs["to"])
            start_hours.append(from_time.hour)
            # If end time is exactly on the hour, we don't need an extra slot
            end_hour = to_time.hour if to_time.minute > 0 else to_time.hour - 1
            end_hours.append(end_hour)

    # Get the range of hours needed (minimum 1 hour if no bookings)
    min_hour = min(start_hours) if start_hours else 0
    max_hour = max(end_hours) if end_hours else 0

    # Create time slots
    time_slots = []
    for hour in range(min_hour, max_hour + 2):  # +2 to include the last hour
        time_slots.append(f"{hour:02d}:00 - {(hour+1):02d}:00")

    # Add a row for each time slot
    for time_slot in time_slots:
        slot_start = int(time_slot.split(":")[0])
        slot_end = slot_start + 1

        table_row = [""] * (days + 1)
        table_row[0] = time_slot

        # Check each day's bookings
        for day_idx in range(days):
            day_bookings = daily_bookings[day_idx]
            cell_bookings = []

            # Sort bookings by start time for this day
            day_bookings.sort(key=lambda b: parser.parse(b["attributes"]["from"]))

            for booking in day_bookings:
                attrs = booking["attributes"]
                from_time = parser.parse(attrs["from"])
                to_time = parser.parse(attrs["to"])

                # Check if booking overlaps with this time slot
                booking_start_hour = from_time.hour
                booking_end_hour = to_time.hour

                if booking_start_hour < slot_end and booking_end_hour > slot_start:
                    title = attrs["title"]
                    name = attrs["name"]

                    # Append the title if it exists, otherwise show name
                    cell_info = f"{name.strip()}: {title.strip()}" if title is not None else name.strip()

                    # Show name only in the first slot of the booking
                    cell_text = (
                        cell_info
                        if slot_start == booking_start_hour
                        else "-" * len(cell_info)
                    )

                    cell_bookings.append(cell_text)

            if cell_bookings:
                table_row[day_idx + 1] = "\n".join(cell_bookings)

        table.add_row(*table_row)

    return table


@app.command()
def show_weekly_schedule(
    token: Optional[str] = typer.Option(
        None, help="Cobot API access token (overrides settings)"
    ),
    resource_id: Optional[str] = typer.Argument(
        None,
        help="Resource ID to show schedule for (uses default from settings if not specified)",
    ),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show"),
):
    """Show a weekly schedule for a specific resource with days as columns."""
    try:
        now = datetime.now(tzutc())
        from_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = from_date + timedelta(days=days)

        with console.status("Fetching schedule..."):
            used_resource_id = (
                resource_id or str(settings.default_resource_id)
                if settings.default_resource_id
                else None
            )
            bookings = fetch_bookings(token, from_date, to_date, used_resource_id)

        if not bookings:
            console.print(
                "No bookings found for the specified resource.", style="yellow"
            )
            return

        table = create_weekly_table(bookings, from_date, days)
        console.print(table)

    except requests.exceptions.HTTPError as e:
        console.print(f"Error: Failed to fetch bookings. {str(e)}", style="red")
    except Exception as e:
        console.print(f"Error: {str(e)}", style="red")


def fetch_resources(token: Optional[str] = None) -> list:
    """Fetch resources from Cobot API."""
    headers = {
        "Authorization": f"Bearer {token or settings.access_token}",
        "Accept": "application/vnd.api+json",
    }

    url = f"{settings.api_base}/spaces/{settings.space_id}/resources"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]


def create_resources_table(resources: list, show_description: bool = False) -> Table:
    """Create a rich table for resources."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    if show_description:
        table.add_column("Description")
    table.add_column("Capacity")
    table.add_column("Available")

    for resource in resources:
        attrs = resource["attributes"]
        resource_id = resource["id"]
        name = attrs.get("name", "N/A")
        capacity = str(attrs.get("capacity", "N/A"))
        available = "✓" if attrs.get("available", False) else "✗"

        if show_description:
            description = attrs.get("description", "N/A")
            table.add_row(resource_id, name, description, capacity, available)
        else:
            table.add_row(resource_id, name, capacity, available)

    return table


@app.command()
def list_resources(
    token: Optional[str] = typer.Option(
        None, help="Cobot API access token (overrides settings)"
    ),
    show_description: bool = typer.Option(
        False, "--description", "-d", help="Show resource descriptions"
    ),
):
    """List all resources in your coworking space."""
    try:
        with console.status("Fetching resources..."):
            resources = fetch_resources(token)

        if not resources:
            console.print("No resources found.", style="yellow")
            return

        table = create_resources_table(resources, show_description)
        console.print(table)

    except requests.exceptions.HTTPError as e:
        console.print(f"Error: Failed to fetch resources. {str(e)}", style="red")
    except Exception as e:
        console.print(f"Error: {str(e)}", style="red")


def main():
    app()
