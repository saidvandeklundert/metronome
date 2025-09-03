from typing import Optional
import subprocess
from dataclasses import dataclass

from metronome import APP_CONTEXT, TaskRegistry, TaskInterval


@dataclass
class CPUState:
    """
    CPU state percentages based on the interval since the last refresh.

    As  a default, percentages for these individual categories are displayed.  Where two labels are shown below, those for more recent kernel versions
    are shown first.
        us, user    : time running un-niced user processes
        sy, system  : time running kernel processes
        ni, nice    : time running niced user processes
        id, idle    : time spent in the kernel idle handler
        wa, IO-wait : time waiting for I/O completion
        hi : time spent servicing hardware interrupts
        si : time spent servicing software interrupts
        st : time stolen from this vm by the hypervisor

    Example line:

    %Cpu(s):  0.0 us, 14.3 sy,  0.0 ni, 85.7 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
    """

    user: float
    system: float
    nice: float
    idle: float
    wait: float
    hardware_interrupts: float
    software_interrupts: float
    st: float


def parse_top(output: str) -> Optional[CPUState]:
    """
    Parses the output of the 'top -n 1 -b' command into an instance of CPUState.
    """
    for line in output.splitlines():
        if line and line.startswith("%Cpu(s):") and line.endswith("0.0 st"):
            chunks = line.split()
            return CPUState(
                user=float(chunks[1]),
                system=float(chunks[3]),
                nice=float(chunks[5]),
                idle=float(chunks[7]),
                wait=float(chunks[9]),
                hardware_interrupts=float(chunks[11]),
                software_interrupts=float(chunks[13]),
                st=float(chunks[15]),
            )


def get_cpu_info() -> Optional[CPUState]:
    """
    Retrieve the device CPU information using the 'top -n 1 -b' command.
    """
    try:
        # TODO: outside container image, run "sudo docker exec -it sonic-host free -m"
        result = subprocess.run(["top", "-n 1", "-b"], capture_output=True, text=True)

        if result.returncode == 0:
            return parse_top(result.stdout)
        else:
            APP_CONTEXT.logger.log_error(f"Error running command: {result.stderr}")

    except Exception as e:
        APP_CONTEXT.logger.log_error(f"running and parsing 'free -m': {str(e)}")


@TaskRegistry.register(interval=TaskInterval.THIRTY_SECONDS)
def task_set_cpu_usage():
    """
    Retrieve the CPU usage that is avaialble on the device and populate STATE_DB with
    this value.
    """
    APP_CONTEXT.logger.log_warning("running task_set_free_memory")
    cpu_state = get_cpu_info()
    if cpu_state is None:
        return
    APP_CONTEXT.custom_table.set(
        "CPU",
        [
            ("cpu_user", str(round(cpu_state.user, 2))),
            ("cpu_system", str(round(cpu_state.system, 2))),
            ("cpu_idle", str(round(cpu_state.idle, 2))),
        ],
    )
