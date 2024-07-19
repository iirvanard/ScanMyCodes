import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None

    def on_any_event(self, event):
        if event.event_type in ('modified', 'created', 'moved'):
            print(f"Perubahan terdeteksi: {event.src_path}. Memulai ulang worker Celery...")
            if self.process:
                self.process.terminate()
                self.process.wait()
            self.process = subprocess.Popen(self.command, shell=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python celery_reloader.py <celery_command>")
        sys.exit(1)

    celery_command = sys.argv[1]
    path_to_watch = '.'  # Atur direktori yang ingin Anda pantau

    event_handler = ReloadHandler(celery_command)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()