# social_analyzer_v2.py

import sys
import re
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import print

# Initialize the rich console for nice output
console = Console()

# --- Data Models ---
class Profile:
    def __init__(self, platform, url, score=0, data=None):
        self.platform = platform
        self.url = url
        self.score = score
        self.data = data if data else {}

def get_query_input():
    console.print(Panel(
        Text("Welcome to the Social Media Analyzer!", style="bold magenta"),
        title="[bold blue]Social Analyzer Tool[/bold blue]",
        border_style="blue"
    ))
    query = input("Please enter a username, phone number, or email to search: ")
    if not query:
        console.print("[bold red]No input provided. Exiting.[/bold red]")
        sys.exit(1)
    return query.strip()

# --- Search Modules ---

def github_search(query):
    api_url = f"https://api.github.com/users/{query}"
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            profile = Profile("GitHub", user_data.get('html_url'), score=10) # 10 points for a confirmed profile
            profile.data = {
                "name": user_data.get('name'),
                "bio": user_data.get('bio'),
                "followers": user_data.get('followers'),
                "repos": user_data.get('public_repos')
            }
            return profile
    except requests.exceptions.RequestException:
        pass
    return None

def leetcode_search(query):
    profile_url = f"https://leetcode.com/{query}/"
    try:
        response = requests.get(profile_url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for a specific element that exists on a real profile page
            if soup.find("div", class_="dark:text-dark-label-2 text-label-2"):
                # You can try to scrape more data here
                return Profile("LeetCode", profile_url, score=5) # 5 points for a confirmed profile
    except requests.exceptions.RequestException:
        pass
    return None

def url_based_search(platform, base_url, query, not_found_indicators):
    profile_url = base_url.format(query)
    try:
        response = requests.get(profile_url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            if any(indicator in page_text for indicator in not_found_indicators):
                return None # Profile not found
            return Profile(platform, profile_url, score=5)
    except requests.exceptions.RequestException:
        pass
    return None

def search_x_linkedin_instagram(query, platform):
    console.print(f"[bold yellow]🔍 Cannot perform a reliable search for {platform}.[/bold yellow]")
    console.print("[italic dim]   Access to this platform's public data requires an API key or is heavily restricted to prevent scraping.[/italic dim]")
    console.print("[italic dim]   A real-world OSINT tool would require authentication here. Skipping for now.[/italic dim]")
    return None

# --- Main Search Logic ---

def search_all_platforms(query):
    profiles = []

    # Determine input type
    if "@" in query and "." in query:
        console.print("\n[bold yellow]🔍 Input detected as an Email. Searching...[/bold yellow]")
        # Placeholder for email search logic
        profiles.append(Profile("Email (Mock)", f"mailto:{query}", score=5, data={"status": "Public data found"}))
    elif re.match(r"^\+?\d[\d\s-]{7,}\d$", query):
        console.print("\n[bold yellow]🔍 Input detected as a Phone Number. Searching...[/bold yellow]")
        # Placeholder for phone number search logic
        profiles.append(Profile("Phone (Mock)", f"tel:{query}", score=5, data={"status": "Public data found"}))
    else:
        # Assume it's a username or name
        console.print("\n[bold yellow]🔍 Input detected as a Username. Searching...[/bold yellow]")

        # Run dedicated search functions
        profiles.append(github_search(query))
        profiles.append(leetcode_search(query))
        
        # URL-based searches with smarter verification
        profiles.append(url_based_search("GitLab", "https://gitlab.com/{}/", query, ["404", "page not found"]))
        profiles.append(url_based_search("Codeforces", "https://codeforces.com/profile/{}/", query, ["user not found"]))
        profiles.append(url_based_search("Reddit", "https://www.reddit.com/user/{}/", query, ["page not found", "username not found"]))
        profiles.append(url_based_search("Stack Overflow", "https://stackoverflow.com/users/{}/", query, ["page not found", "user not found"]))
        
        # Difficult platforms
        profiles.append(search_x_linkedin_instagram(query, "X"))
        profiles.append(search_x_linkedin_instagram(query, "LinkedIn"))
        profiles.append(search_x_linkedin_instagram(query, "Instagram"))

    return [p for p in profiles if p is not None]

# --- Reporting and Scoring ---

def generate_report(profiles, query):
    console.print(Panel(
        f"[bold cyan]Final Report for: [dim]{query}[/dim][/bold cyan]",
        title="[bold green]Search Complete[/bold green]",
        border_style="green"
    ))

    if not profiles:
        console.print(f"[bold red]❌ No profiles found for {query}.[/bold red]")
        return

    # Check for name consistency and generate a score
    total_score = 0
    all_names = []
    
    # Extract names and calculate total score
    for profile in profiles:
        total_score += profile.score
        if 'name' in profile.data and profile.data['name']:
            all_names.append(profile.data['name'])

    # Calculate name consistency
    name_consistency_score = 0
    if len(all_names) > 1:
        most_common_name = max(set(all_names), key=all_names.count)
        for name in all_names:
            if name == most_common_name:
                name_consistency_score += 5

    final_score = total_score + name_consistency_score
    
    console.print(f"Overall Relevance Score: [bold magenta]{final_score}[/bold magenta]\n")
    if all_names:
        console.print(f"Name Consistency Found: [bold]{most_common_name}[/bold] (from {len(all_names)} sources)\n")
    
    table = Table(title="[bold yellow]Found Profiles[/bold yellow]", show_lines=True)
    table.add_column("Platform", style="bold green")
    table.add_column("URL", style="link")
    table.add_column("Relevance Score", style="bold cyan")
    table.add_column("Details", style="dim")

    for profile in profiles:
        details = ""
        if profile.data:
            details = ", ".join([f"{k}: {v}" for k, v in profile.data.items() if v])
        
        table.add_row(profile.platform, profile.url, str(profile.score), details)
    
    console.print(table)
    print("\n[dim]Note: A higher relevance score indicates a stronger correlation of public data across platforms.[/dim]")

def main():
    try:
        query = get_query_input()
        found_profiles = search_all_platforms(query)
        generate_report(found_profiles, query)
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user.[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()