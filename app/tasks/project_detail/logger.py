import errno
import os
import uuid
import logging
from app import app  # Pastikan import ini sudah sesuai dengan struktur aplikasi Anda

class LoggerSetup:
    def __init__(self, task_id, proj_name, user):
        self.task_id = task_id
        self.proj_name = proj_name
        self.user = user
        self.logger = logging.getLogger(task_id)
        self.setup_logger()

    def setup_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        self.logger.setLevel(logging.INFO)

        log_file_path = self._get_log_file_path()
        fh = logging.FileHandler(log_file_path)
        fh.setFormatter(formatter)

        # Hapus handler yang ada dan tambahkan yang baru
        for handler in list(self.logger.handlers):
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)
        
        # Tambahkan handler ke logger
        self.logger.addHandler(fh)

        self.logger.info(f"Task {self.task_id} started for project {self.proj_name} by user {self.user}. [done]")

    def _get_log_file_path(self):
        log_dir = self._get_log_directory()
        self.filename = f"{uuid.uuid4().hex}.log"
        return os.path.join(log_dir, self.filename)

    def _get_log_directory(self):
        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log")
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return dir_path

    def get_logger(self):
        return self.logger, self.filename

    @staticmethod
    def get_logger_filename(task_id, path):
        logger = logging.getLogger(task_id)
        if not logger.handlers:
            fh = logging.FileHandler(path)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)
    
        return logger
