import subprocess
import logging
import os
import sys

from flask import app

# Konfigurasi logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output ke konsol
        logging.FileHandler("realtime_scan.log", mode="w")  # Simpan ke file log
    ]
)

def split_url(url: str) -> str:
    last_slash_index = url.rfind("/")
    last_suffix_index = url.rfind(".git")
    if last_suffix_index < 0:
        last_suffix_index = len(url)

    if last_slash_index < 0 or last_suffix_index <= last_slash_index:
        raise Exception("Badly formatted url {}".format(url))

    return url[:last_slash_index].split("/")[-1], url[last_slash_index +
                                                      1:last_suffix_index]


def run_wsl_command(entry_point, output_path, runner_script):
    """
    Menjalankan runner.sh dalam WSL untuk menjalankan Bearer scan.

    :param entry_point: Path ke direktori proyek yang akan dipindai.
    :param output_path: Path lengkap untuk menyimpan hasil scan (termasuk nama file JSON).
    :param tools: Nama alat yang akan dijalankan, default "bearer".
    """


    if not os.path.exists(runner_script):
        logging.error(f"{runner_script} runner script not found: {runner_script}")
        return

    try:
        result = subprocess.run(
            f"bash {runner_script} {entry_point}", shell=True, text=True, capture_output=True
        )

        if result.stderr:
            logging.warning(f"Command error output: {result.stderr}")

        with open(output_path, "w") as file:
            file.write(result.stdout)

    except Exception as e:
        logging.error(f"Error running {runner_script}: {e}")

# # Contoh penggunaan
# if __name__ == "__main__":

#     run_wsl_command("/home/iirvanard/projects/ScanMyCodes/app/", "/home/iirvanard/projects/ScanMyCodes/test/test.json")