from metronome.models import SonicDb
import os
from swsscommon import swsscommon
from sonic_py_common import daemon_base, logger
from sonic_py_common.device_info import run_command

class ApplicationContext:
    def __init__(self):
        self.pid: int = os.getpid()
        self.logger: logger.Logger = logger.Logger("METRONOME")
        self.logger.set_min_log_priority_info()
        self.logger.log_info(f"initializing module as process {self.pid}")
        self.state_db: swsscommon.DBConnector = daemon_base.db_connect(SonicDb.STATE_DB)
        self.custom_table: swsscommon.Table = swsscommon.Table(self.state_db, "_CUSTOM")
        self.appl_db: swsscommon.DBConnector = daemon_base.db_connect(SonicDb.APPL_DB)


APP_CONTEXT = ApplicationContext()
