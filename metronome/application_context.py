from metronome.models import SonicDb
import os
from swsscommon import swsscommon
from sonic_py_common import daemon_base, logger


class ApplicationContext:
    def __init__(self):
        self.pid: int = os.getpid()
        self.logger: logger.Logger = logger.Logger("METRONOME")
        self.logger.set_min_log_priority_info()
        self.logger.log_info(f"initializing module as process {self.pid}")
        self.appl_db: swsscommon.DBConnector = daemon_base.db_connect(
            SonicDb.APPL_DB
        )  # 0
        self.counter_db: swsscommon.DBConnector = daemon_base.db_connect(
            SonicDb.COUNTERS_DB
        )  # 2
        self.state_db: swsscommon.DBConnector = daemon_base.db_connect(
            SonicDb.STATE_DB
        )  # 6
        self.custom_table: swsscommon.Table = swsscommon.Table(self.state_db, "_CUSTOM")
        self.interface_errors_table: swsscommon.Table = swsscommon.Table(
            self.state_db, "_CUSTOM_INTERFACE_ERRORS"
        )


APP_CONTEXT = ApplicationContext()
