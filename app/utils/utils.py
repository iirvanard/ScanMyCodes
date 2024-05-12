import subprocess


def split_url(url: str) -> str:
    last_slash_index = url.rfind("/")
    last_suffix_index = url.rfind(".git")
    if last_suffix_index < 0:
        last_suffix_index = len(url)

    if last_slash_index < 0 or last_suffix_index <= last_slash_index:
        raise Exception("Badly formatted url {}".format(url))

    return url[:last_slash_index].split("/")[-1], url[last_slash_index +
                                                      1:last_suffix_index]


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
