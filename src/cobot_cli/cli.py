#!/usr/bin/env python3
import typer
import requests
from datetime import datetime, timedelta
from typing import Optional
from rich.console import Console
from rich.table import Table
from dateutil import parser
from dateutil.tz import tzutc

app = typer.Typer()
console = Console()

COBOT_API_BASE = "https://api.cobot.me"

def fetch_bookings(token: str, from_date: datetime, to_date: datetime, resource_id: Optional[str] = None) -> list:
    """Fetch bookings from Cobot API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json"
    }
    params = {
        "filter[from]": from_date.isoformat(),
        "filter[to]": to_date.isoformat(),
    }
    
    # The space ID is hardcoded based on the sample data
    space_id = "9cc8fb9aa608530497f20946e1d083ea"
    url = f"{COBOT_API_BASE}/spaces/{space_id}/bookings"
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    bookings = response.json()["data"]
    
    if resource_id:
        bookings = [
            b for b in bookings 
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
        
        table.add_row(
            date,
            time,
            name,
            title,
            resource_id
        )
    
    return table

@app.command()
def get_bookings(
    token: str = typer.Argument(..., help="Cobot API access token"),
    resource_id: Optional[str] = typer.Option(None, "--resource", "-r", help="Specific resource ID to filter"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to fetch bookings for")
):
    """Fetch and display bookings from your coworking space."""
    try:
        now = datetime.now(tzutc())
        from_date = now
        to_date = now + timedelta(days=days)
        
        with console.status("Fetching bookings..."):
            bookings = fetch_bookings(token, from_date, to_date, resource_id)
        
        if not bookings:
            console.print("No bookings found for the specified criteria.", style="yellow")
            return
        
        table = create_bookings_table(bookings)
        console.print(table)
        
    except requests.exceptions.HTTPError as e:
        console.print(f"Error: Failed to fetch bookings. {str(e)}", style="red")
    except Exception as e:
        console.print(f"Error: {str(e)}", style="red")

def create_weekly_table(bookings: list, from_date: datetime, days: int) -> Table:
    """Create a rich table with days as columns and time slots as rows."""
    table = Table(show_header=True, header_style="bold magenta")
    
    # Add columns for time and each day
    table.add_column("Time/Details")
    for i in range(days):
        current_date = from_date + timedelta(days=i)
        table.add_column(current_date.strftime("%Y-%m-%d"))
    
    # Group bookings by day and time
    daily_bookings = {i: [] for i in range(days)}
    for booking in bookings:
        attrs = booking["attributes"]
        from_time = parser.parse(attrs["from"])
        days_diff = (from_time.date() - from_date.date()).days
        if 0 <= days_diff < days:
            daily_bookings[days_diff].append(booking)
    
    # Create rows for each booking
    rows = []
    for day_idx in range(days):
        day_bookings = daily_bookings[day_idx]
        for booking in day_bookings:
            attrs = booking["attributes"]
            from_time = parser.parse(attrs["from"])
            to_time = parser.parse(attrs["to"])
            time_str = f"{from_time.strftime('%H:%M')} - {to_time.strftime('%H:%M')}"
            name = attrs["name"] or "N/A"
            title = attrs["title"] or "N/A"
            
            # Create a row entry
            row_data = {
                "time": time_str,
                "details": f"{name}\n{title}",
                "day_idx": day_idx
            }
            rows.append(row_data)
    
    # Sort rows by time
    rows.sort(key=lambda x: x["time"])
    
    # Add rows to table
    for row in rows:
        table_row = [""] * (days + 1)
        table_row[0] = row["time"]
        table_row[row["day_idx"] + 1] = row["details"]
        table.add_row(*table_row)
    
    return table

@app.command()
def show_weekly_schedule(
    token: str = typer.Argument(..., help="Cobot API access token"),
    resource_id: str = typer.Argument(..., help="Resource ID to show schedule for"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show")
):
    """Show a weekly schedule for a specific resource with days as columns."""
    try:
        now = datetime.now(tzutc())
        from_date = now
        to_date = now + timedelta(days=days)
        
        with console.status("Fetching schedule..."):
            bookings = fetch_bookings(token, from_date, to_date, resource_id)
        
        if not bookings:
            console.print("No bookings found for the specified resource.", style="yellow")
            return
        
        table = create_weekly_table(bookings, from_date, days)
        console.print(table)
        
    except requests.exceptions.HTTPError as e:
        console.print(f"Error: Failed to fetch bookings. {str(e)}", style="red")
    except Exception as e:
        console.print(f"Error: {str(e)}", style="red")

def main():
    app()
