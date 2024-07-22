
import os
import uuid
import logging
from app import app

class LoggerSetup:
    def __init__(self, task_id, proj_name, user):
        self.task_id = task_id
        self.proj_name = proj_name
        self.user = user
        self.logger = logging.getLogger(task_id)
        self.filename = None
        self.setup_logger()

    def setup_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        self.logger.setLevel(logging.INFO)

        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log")
        os.makedirs(dir_path, exist_ok=True)
        self.filename = f"{uuid.uuid4().hex}.log"
        log_file_path = os.path.join(dir_path, self.filename)
        
        fh = logging.FileHandler(log_file_path)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        self.logger.info(f"Task {self.task_id} started for project {self.proj_name} by user {self.user}.  [done]")

    def get_logger(self):
        return self.logger, self.filename
