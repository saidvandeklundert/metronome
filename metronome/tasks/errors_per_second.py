from metronome import APP_CONTEXT

from typing import Dict, Tuple, Set

from copy import deepcopy


from metronome import TaskRegistry, TaskInterval

INTERVAL = TaskInterval.THIRTY_SECONDS

Name = str
Oid = str
State = str


NAME_TO_OID: Dict[Name, Oid] = {}
OID_TO_NAME: Dict[Oid, Name] = {}
PORT_ERROR_MAPPING: Dict[Name, Dict] = {}

SAI_PORT_STAT_IF_OUT_ERRORS = "SAI_PORT_STAT_IF_OUT_ERRORS"
SAI_PORT_STAT_IF_OUT_DISCARDS = "SAI_PORT_STAT_IF_OUT_DISCARDS"
SAI_PORT_STAT_IF_IN_FEC_NOT_CORRECTABLE_FRAMES = (
    "SAI_PORT_STAT_IF_IN_FEC_NOT_CORRECTABLE_FRAMES"
)
SAI_PORT_STAT_IF_IN_FEC_CORRECTABLE_FRAMES = (
    "SAI_PORT_STAT_IF_IN_FEC_CORRECTABLE_FRAMES"
)
SAI_PORT_STAT_IF_IN_ERRORS = "SAI_PORT_STAT_IF_IN_ERRORS"
SAI_PORT_STAT_IF_IN_DISCARDS = "SAI_PORT_STAT_IF_IN_DISCARDS"
SAI_PORT_STAT_ETHER_TX_OVERSIZE_PKTS = "SAI_PORT_STAT_ETHER_TX_OVERSIZE_PKTS"
SAI_PORT_STAT_ETHER_STATS_UNDERSIZE_PKTS = "SAI_PORT_STAT_ETHER_STATS_UNDERSIZE_PKTS"
SAI_PORT_STAT_ETHER_STATS_JABBERS = "SAI_PORT_STAT_ETHER_STATS_JABBERS"
SAI_QUEUE_STAT_DROPPED_PACKETS = "SAI_QUEUE_STAT_DROPPED_PACKETS"
SAI_QUEUE_STAT_DROPPED_BYTES = "SAI_QUEUE_STAT_DROPPED_BYTES"

INTERESTING_ERRORS: Set[str] = {
    SAI_PORT_STAT_IF_OUT_ERRORS,
    SAI_PORT_STAT_IF_OUT_DISCARDS,
    SAI_PORT_STAT_IF_IN_FEC_NOT_CORRECTABLE_FRAMES,
    SAI_PORT_STAT_IF_IN_FEC_CORRECTABLE_FRAMES,
    SAI_PORT_STAT_IF_IN_ERRORS,
    SAI_PORT_STAT_IF_IN_DISCARDS,
    SAI_PORT_STAT_ETHER_TX_OVERSIZE_PKTS,
    SAI_PORT_STAT_ETHER_STATS_UNDERSIZE_PKTS,
    SAI_PORT_STAT_ETHER_STATS_JABBERS,
    SAI_QUEUE_STAT_DROPPED_PACKETS,
    SAI_QUEUE_STAT_DROPPED_BYTES,
}
ERRORS_INIT = {k: 0 for k in INTERESTING_ERRORS}


def new_to_old(port_error_mapping: Dict) -> None:
    """
    Copy the most recent counters to the old counters and zeroise the new counters.
    """
    for v in port_error_mapping.values():
        v["old"] = v["new"]
        v["new"] = deepcopy(ERRORS_INIT)


def add_per_second_rate(port_error_mapping: Dict, interval: int) -> None:
    """
    Based on the old and the new value, calculate the per-second error rate.
    """
    for interface_name in port_error_mapping.keys():
        for error_name in INTERESTING_ERRORS:
            new_err = port_error_mapping[interface_name]["new"][error_name]
            old_err = port_error_mapping[interface_name]["old"][error_name]
            per_second = (new_err - old_err) / interval
            port_error_mapping[interface_name]["per-second"][error_name] = int(
                per_second
            )
            if per_second != 0:
                APP_CONTEXT.logger.log_error(
                    f"interface errors on {interface_name} for {error_name}: {per_second} per second",
                )
    return None


def update_interface_errors(interface_name: str, error_data: dict):
    """
    Update interface error data in the custom table
    """

    fvs = [(k, str(v)) for k, v in error_data.items()]

    APP_CONTEXT.interface_errors_table.set(interface_name, fvs)
    APP_CONTEXT.logger.log_debug(f"Updated interface errors for {interface_name}")


def initialize_counters():
    """
    Initialize counters.
    """
    for name, oid in APP_CONTEXT.counter_db.hgetall("COUNTERS_PORT_NAME_MAP").items():
        NAME_TO_OID[name] = oid
        OID_TO_NAME[oid] = name
        PORT_ERROR_MAPPING[name] = {
            "old": deepcopy(ERRORS_INIT),
            "new": deepcopy(ERRORS_INIT),
            "per-second": deepcopy(ERRORS_INIT),
        }


@TaskRegistry.register(interval=INTERVAL)
def task_set_errors_per_second():
    """
    This task follows the following algorithm:
    - initialize mappings between OIDs and port names
    - periodically get the counters for every port on the device
    - when the counters are collected, move the current counters to the previous ones and populate new counters
    - if the previous counters exist and are non-zero, compute and populate the erorr rate counter


    All ports are taken into consideration. To count errors incrementing on flapping ports.
    """
    APP_CONTEXT.logger.log_info("running task_set_errors_per_second")

    # initialize OR move new values to old:
    if not NAME_TO_OID:
        initialize_counters()
        return
    else:
        new_to_old(PORT_ERROR_MAPPING)
    # iterate all OIDs and fetch the errors. Set all interesting error values to 'new':
    for oid, interface_name in OID_TO_NAME.items():
        for counter_name, counter_value in APP_CONTEXT.counter_db.hgetall(
            f"COUNTERS:{oid}"
        ).items():
            if counter_name in INTERESTING_ERRORS:
                PORT_ERROR_MAPPING[interface_name]["new"][counter_name] = int(
                    counter_value
                )
    # add error per second:
    add_per_second_rate(PORT_ERROR_MAPPING, INTERVAL.value)
    # update table
    for interface_name in NAME_TO_OID.keys():
        update_interface_errors(
            interface_name=interface_name,
            error_data=PORT_ERROR_MAPPING[interface_name]["per-second"],
        )
