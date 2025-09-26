import json
import typer
import httpx
from pathlib import Path
from api.settings import get_settings

# Initialize the Typer CLI app
app = typer.Typer()


BASE_URL = "http://localhost:5000"  # Adjust this to the actual API URL

# Load parameters from the JSON file
def load_params(file_path: Path):
    """Loads job parameters from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        typer.echo(f"Error reading JSON file: {e}")
        raise typer.Exit(code=1)

# Function to send job-start requests
def send_request(param):
    """Sends an HTTP POST request to start a job with the given parameters."""
    api_name = param.get("api")
    url = f"{BASE_URL}/job-start/{api_name.upper()}"
    typer.echo(f"Sending request to {url} with parameters: {param}")

    
    try:
        response = httpx.post(url, json=param)
        response.raise_for_status()
        typer.echo(f"Job started successfully: {response.json()}")
    except httpx.HTTPStatusError as e:
        typer.echo(f"HTTP error occurred: {e.response.text}")
    except Exception as e:
        typer.echo(f"Request failed: {e}")

@app.command()
def run_jobs(params_file: str):
    """Reads a JSON file and starts jobs via API requests."""
    typer.echo(f"Loading parameters from {params_file}...")
    
    params = load_params(Path(params_file))
    
    for param in params:
        send_request(param)

if __name__ == "__main__":
    typer.run(run_jobs)