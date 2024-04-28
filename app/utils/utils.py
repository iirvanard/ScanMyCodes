from urllib.parse import urlparse
import subprocess

def split_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'github.com':
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            repo_owner = path_parts[0]
            repo_name = path_parts[1].rstrip('.git')
            return repo_owner, repo_name
    return None, None

def run_wsl_command(source_path, filename):
    # # Command to run WSL
    wsl_command = f"C:/bearer/bearer.exe scan {source_path} --format json --output {filename}"

    # Run the command and capture output
    result = subprocess.run(wsl_command,
                            shell=True,
                            capture_output=True,
                            text=True)
    print(str(result))
    # Return the output
    return result.stdout.strip()
# repo_owner, repo_name = get_repo_info_from_url(url) #use this