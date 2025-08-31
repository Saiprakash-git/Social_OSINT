# social_analyzer.py (Updated Code)

import sys
import re
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich import print

# Initialize the rich console for nice output
console = Console()

def github_search(username):
    # ... (Keep the existing github_search function as it is, as it's API-based)
    api_url = f"https://api.github.com/users/{username}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        
        user_data = response.json()
        
        if 'id' in user_data:
            console.print(Panel(f"[bold cyan]GitHub Profile Found[/bold cyan]", border_style="green"))
            
            table = Table(show_header=False, show_lines=True, title=f"GitHub Profile: [bold]{user_data.get('login')}[/bold]")
            table.add_column("Key", style="bold")
            table.add_column("Value")
            
            table.add_row("Username", user_data.get('login'))
            table.add_row("Name", user_data.get('name', 'N/A'))
            table.add_row("Bio", user_data.get('bio', 'N/A'))
            table.add_row("Location", user_data.get('location', 'N/A'))
            table.add_row("Public Repos", str(user_data.get('public_repos', 'N/A')))
            table.add_row("Followers", str(user_data.get('followers', 'N/A')))
            table.add_row("Following", str(user_data.get('following', 'N/A')))
            table.add_row("Profile URL", user_data.get('html_url'))
            
            console.print(table)
            
            avatar_url = user_data.get('avatar_url')
            if avatar_url:
                console.print(f"Profile Picture: [link={avatar_url}]{avatar_url}[/link]\n")
        else:
            console.print(f"[bold red]❌ No GitHub profile found for username: {username}[/bold red]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ Error connecting to GitHub API: {e}[/bold red]")


def verify_profile_existence(response_text, not_found_indicators):
    """
    Checks the page content for 'not found' indicators.
    """
    if "404" in response_text or "not found" in response_text.lower():
        return False
    
    # Check for platform-specific indicators
    for indicator in not_found_indicators:
        if indicator.lower() in response_text.lower():
            return False
            
    return True

def url_search_smart(platform_name, base_url, username, not_found_indicators=None):
    """
    Smarter search function that verifies profile existence by parsing content.
    """
    if not_found_indicators is None:
        not_found_indicators = []
        
    profile_url = base_url.format(username)
    
    try:
        response = requests.get(profile_url, timeout=5)
        
        # Check HTTP status code first
        if response.status_code == 404:
            console.print(f"[bold red]❌ No {platform_name} profile found.[/bold red]")
            return False

        # If it's not a 404, analyze the page content for 'not found' indicators
        if verify_profile_existence(response.text, not_found_indicators):
            console.print(f"[bold green]✅ {platform_name} profile found:[/bold green] [link={profile_url}]{profile_url}[/link]")
            return True
        else:
            console.print(f"[bold red]❌ No {platform_name} profile found.[/bold red]")
            return False
            
    except requests.exceptions.RequestException:
        console.print(f"[bold red]❌ Could not connect to {platform_name}.[/bold red]")
        return False

def get_query_input():
    # ... (Keep this function as it is)
    console.print(Panel(
        Text("Welcome to the Social Media Analyzer!", style="bold magenta"),
        title="[bold blue]Social Analyzer Tool[/bold blue]",
        border_style="blue"
    ))
    
    query = Prompt.ask("Please enter a [bold green]username[/bold green], [bold green]phone number[/bold green], or [bold green]email[/bold green] to search")
    
    if not query:
        console.print("[bold red]No input provided. Exiting.[/bold red]")
        sys.exit(1)
        
    return query.strip()
# Add this function somewhere in your script
def search_email(email):
    """
    Searches for information linked to an email.
    """
    console.print(f"Searching for data related to email: {email}")
    
    # This is a mock function. In a real project, you would
    # call a public API or a service like Hunter.io or similar
    # to find associated public data.
    
    # For now, let's pretend we found some data from a mock API
    # that links an email to a social profile.
    
    mock_found = {
        "user@example.com": {
            "name": "John Doe",
            "linked_profiles": ["linkedin.com/in/johndoe", "github.com/johndoe"]
        }
    }
    
    if email in mock_found:
        data = mock_found[email]
        console.print(Panel(
            f"[bold green]✅ Data found for {email}[/bold green]",
            border_style="green"
        ))
        table = Table(title="Email Search Results")
        table.add_column("Key", style="bold")
        table.add_column("Value")
        table.add_row("Name", data["name"])
        table.add_row("Linked Profiles", ", ".join(data["linked_profiles"]))
        console.print(table)
    else:
        console.print(f"[bold red]❌ No public data found for email: {email}[/bold red]")
        
# Add this function somewhere in your script
def search_phone(phone_number):
    """
    Searches for information linked to a phone number.
    """
    console.print(f"Searching for data related to phone number: {phone_number}")

    # This is a mock function. Real-world phone number searches often
    # require accessing specific, often paid, OSINT tools.
    
    # We will simulate a result from a public service like Truecaller.
    
    mock_found = {
        "9876543210": {
            "name": "Jane Smith",
            "carrier": "T-Mobile",
            "linked_profiles": ["Truecaller Profile: truecaller.com/jane_smith"]
        }
    }
    
    normalized_phone = phone_number.replace(" ", "").replace("-", "")
    
    if normalized_phone in mock_found:
        data = mock_found[normalized_phone]
        console.print(Panel(
            f"[bold green]✅ Data found for {phone_number}[/bold green]",
            border_style="green"
        ))
        table = Table(title="Phone Number Search Results")
        table.add_column("Key", style="bold")
        table.add_column("Value")
        table.add_row("Name", data["name"])
        table.add_row("Carrier", data["carrier"])
        table.add_row("Linked Profiles", ", ".join(data["linked_profiles"]))
        console.print(table)
    else:
        console.print(f"[bold red]❌ No public data found for phone number: {phone_number}[/bold red]")
# Updated search_all_platforms function
def search_all_platforms(query):
    console.print(Panel(
        f"[bold cyan]Starting search for: [dim]{query}[/dim][/bold cyan]",
        title="[bold green]Search in Progress[/bold green]",
        border_style="green"
    ))
    
    # Simple logic to determine the type of input
    if re.match(r"^\+?\d[\d\s-]{7,}\d$", query):
        console.print("\n[bold yellow]🔍 Input detected as a Phone Number. Searching...[/bold yellow]")
        search_phone(query)
        
    elif "@" in query and "." in query:
        console.print("\n[bold yellow]🔍 Input detected as an Email. Searching...[/bold yellow]")
        search_email(query)
        
    else:
        # Assuming it's a username or name
        console.print("\n[bold yellow]🔍 Input detected as a Username or Name. Searching...[/bold yellow]")
        
        # GitHub Search (API-based)
        github_search(query)
        
        # Smarter URL-based Searches for other platforms
        console.print(Panel("🌐 Checking for profiles on various websites...", border_style="dim"))
        
        # LeetCode: "User not found"
        url_search_smart("LeetCode", "https://leetcode.com/{}/", query, not_found_indicators=["user not found", "userNotFound"])

        # GitLab: "404 page" (which is the default behavior for non-existent users)
        url_search_smart("GitLab", "https://gitlab.com/{}/", query, not_found_indicators=["404", "page not found"])

        # Codeforces: "User <username> not found"
        url_search_smart("Codeforces", "https://codeforces.com/profile/{}/", query, not_found_indicators=["User not found"])

        # Reddit: "page not found"
        url_search_smart("Reddit", "https://www.reddit.com/user/{}/", query, not_found_indicators=["page not found", "username not found"])
        
        console.print(Panel(f"[bold green]Search Complete![/bold green]", border_style="green"))



def main():
    # ... (Keep this function as it is)
    try:
        query = get_query_input()
        search_all_platforms(query)
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user.[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()