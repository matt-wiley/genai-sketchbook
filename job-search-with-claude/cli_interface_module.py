import click
import logging
import yaml
from pathlib import Path
import re
from data_management_module import DataManager
from api_integration_module import APIIntegration
from ai_job_matching_module import AIJobMatcher
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

console = Console()

CONFIG_PATH = 'config.yaml'

def load_config(config_path=CONFIG_PATH):
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        console.print(f"[red]Error: Configuration file '{config_path}' not found.[/red]")
        exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing configuration file: {e}[/red]")
        exit(1)

def save_config(config, config_path=CONFIG_PATH):
    try:
        with open(config_path, 'w') as config_file:
            yaml.dump(config, config_file, default_flow_style=False)
        console.print("[green]Configuration saved successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Error saving configuration: {e}[/red]")

CONFIG = load_config()

def validate_email(ctx, param, value):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise click.BadParameter('Invalid email address')
    return value

def validate_user_id(ctx, param, value):
    if value <= 0:
        raise click.BadParameter('User ID must be a positive integer')
    return value

@click.group()
@click.option('--debug/--no-debug', default=False, help="Enable debug logging")
def cli(debug):
    log_level = logging.DEBUG if debug else logging.INFO
    try:
        logging.basicConfig(level=log_level, 
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=CONFIG['logging']['file'])
    except Exception as e:
        console.print(f"[yellow]Warning: Unable to configure logging. {str(e)}[/yellow]")

@cli.command()
@click.option('--name', prompt='Your name', help='Your full name')
@click.option('--email', prompt='Your email', help='Your email address', callback=validate_email)
@click.option('--skills', prompt='Your skills', help='Your skills (comma-separated)')
@click.option('--experience', prompt='Your experience', help='Brief description of your experience')
def create_profile(name, email, skills, experience):
    """Create a new user profile."""
    try:
        dm = DataManager(CONFIG['database']['name'])
        profile = {
            'name': name,
            'email': email,
            'skills': skills,
            'experience': experience,
            'resume_text': ''
        }
        if dm.add_user_profile(profile):
            console.print("[green]Profile created successfully![/green]")
        else:
            console.print("[red]Failed to create profile. Please try again.[/red]")
    except Exception as e:
        console.print(f"[red]An error occurred while creating the profile: {str(e)}[/red]")
    finally:
        dm.close()

@cli.command()
@click.option('--user-id', type=int, prompt='Your user ID', help='Your user ID', callback=validate_user_id)
def view_profile(user_id):
    """View your user profile."""
    try:
        dm = DataManager(CONFIG['database']['name'])
        profile = dm.get_user_profile(user_id)
        if profile:
            table = Table(title=f"Profile for User {user_id}")
            for key, value in profile.items():
                table.add_row(key.capitalize(), str(value))
            console.print(table)
        else:
            console.print("[yellow]Profile not found. Please check the user ID and try again.[/yellow]")
    except Exception as e:
        console.print(f"[red]An error occurred while retrieving the profile: {str(e)}[/red]")
    finally:
        dm.close()

@cli.command()
@click.option('--what', prompt='Job title or keywords', help='Job title or keywords to search for')
@click.option('--where', default=CONFIG['job_search']['default_location'], help='Job location')
@click.option('--days', default=CONFIG['job_search']['default_days_old'], type=int, help='Number of days to look back')
@click.option('--max-jobs', default=CONFIG['job_search']['max_jobs_per_search'], type=int, help='Maximum number of jobs to fetch')
def fetch_jobs(what, where, days, max_jobs):
    """Fetch jobs from the API and store them in the database."""
    try:
        api = APIIntegration(
            CONFIG['api']['adzuna']['app_id'],
            CONFIG['api']['adzuna']['api_key'],
            CONFIG['database']['name']
        )
        stored_jobs = api.fetch_and_store_jobs(what, where, days_old=days, max_jobs=max_jobs)
        console.print(f"[green]Stored {stored_jobs} jobs.[/green]")
    except Exception as e:
        console.print(f"[red]An error occurred while fetching jobs: {str(e)}[/red]")
    finally:
        api.close()

@cli.command()
@click.option('--user-id', type=int, prompt='Your user ID', help='Your user ID', callback=validate_user_id)
@click.option('--top-n', default=CONFIG['user']['default_top_matches'], type=int, help='Number of top matches to display')
def match_jobs(user_id, top_n):
    """Find top job matches for a user."""
    try:
        matcher = AIJobMatcher(CONFIG['database']['name'])
        top_jobs = matcher.rank_jobs_for_user(user_id, top_n)
        
        if top_jobs:
            table = Table(title=f"Top {top_n} Job Matches")
            table.add_column("Title", style="cyan")
            table.add_column("Company", style="magenta")
            table.add_column("Location", style="green")
            table.add_column("Match Score", style="yellow")
            
            for job, score in top_jobs:
                table.add_row(job['title'], job['company'], job['location'], f"{score:.2f}")
            
            console.print(table)
        else:
            console.print("[yellow]No job matches found. Try updating your profile or fetching more jobs.[/yellow]")
    except Exception as e:
        console.print(f"[red]An error occurred while matching jobs: {str(e)}[/red]")
    finally:
        matcher.close()

@cli.command()
@click.option('--user-id', type=int, prompt='Your user ID', help='Your user ID', callback=validate_user_id)
@click.option('--top-n', default=CONFIG['user']['default_skill_recommendations'], type=int, help='Number of skills to recommend')
def recommend_skills(user_id, top_n):
    """Get skill recommendations for a user."""
    try:
        matcher = AIJobMatcher(CONFIG['database']['name'])
        recommended_skills = matcher.get_skill_recommendations(user_id, top_n)
        
        if recommended_skills:
            console.print("[green]Recommended skills to learn:[/green]")
            for skill in recommended_skills:
                console.print(f"- {skill}")
        else:
            console.print("[yellow]No skill recommendations available. Try updating your profile or fetching more jobs.[/yellow]")
    except Exception as e:
        console.print(f"[red]An error occurred while recommending skills: {str(e)}[/red]")
    finally:
        matcher.close()

@cli.command()
@click.option('--keyword', prompt='Search keyword', help='Keyword to search for in job titles or descriptions')
def search_jobs(keyword):
    """Search for jobs in the database."""
    try:
        dm = DataManager(CONFIG['database']['name'])
        jobs = dm.search_jobs(keyword)
        
        if jobs:
            table = Table(title=f"Job Search Results for '{keyword}'")
            table.add_column("Title", style="cyan")
            table.add_column("Company", style="magenta")
            table.add_column("Location", style="green")
            
            for job in jobs:
                table.add_row(job['title'], job['company'], job['location'])
            
            console.print(table)
        else:
            console.print("[yellow]No jobs found matching the keyword. Try a different search term or fetch more jobs.[/yellow]")
    except Exception as e:
        console.print(f"[red]An error occurred while searching for jobs: {str(e)}[/red]")
    finally:
        dm.close()

@cli.group()
def config():
    """Manage application configuration."""
    pass

@config.command()
def view():
    """View the current configuration."""
    yaml_str = yaml.dump(CONFIG, default_flow_style=False)
    syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
    console.print(syntax)

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value."""
    keys = key.split('.')
    current = CONFIG
    for k in keys[:-1]:
        if k not in current:
            console.print(f"[red]Error: Key '{k}' not found in configuration.[/red]")
            return
        current = current[k]
    
    if keys[-1] not in current:
        console.print(f"[red]Error: Key '{keys[-1]}' not found in configuration.[/red]")
        return
    
    # Convert value to appropriate type
    original_type = type(current[keys[-1]])
    try:
        if original_type == bool:
            value = value.lower() in ('true', 'yes', '1', 'on')
        elif original_type == int:
            value = int(value)
        elif original_type == float:
            value = float(value)
        current[keys[-1]] = value
    except ValueError:
        console.print(f"[red]Error: Invalid value type. Expected {original_type.__name__}.[/red]")
        return

    save_config(CONFIG)
    console.print(f"[green]Updated {key} to {value}[/green]")

@config.command()
def reset():
    """Reset the configuration to default values."""
    default_config = {
        'database': {'name': 'job_search.db'},
        'api': {
            'adzuna': {'app_id': '', 'api_key': ''},
            'jooble': {'api_key': ''}
        },
        'job_search': {
            'default_location': 'London',
            'default_days_old': 30,
            'max_jobs_per_search': 100
        },
        'user': {
            'default_top_matches': 10,
            'default_skill_recommendations': 5
        },
        'logging': {
            'level': 'INFO',
            'file': 'job_search.log'
        }
    }
    save_config(default_config)
    global CONFIG
    CONFIG = default_config
    console.print("[green]Configuration reset to default values.[/green]")

if __name__ == '__main__':
    cli()
