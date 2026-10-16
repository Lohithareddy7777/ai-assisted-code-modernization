# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Runs every morning. Never cleaned up.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils
from statistics import mean

def car_wear(car: dict) -> float | None:
    """Return wear percentage, or None when the service reading is unknown."""
    last_service = car.get("last_service_km")
    if last_service is None:
        return None
    return wear_percent(car["odometer"] - last_service, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict[str, int | float]:
    """Summarize fleet size, service needs, and average known wear."""
    wear_values = [
        wear for car in fleet
        if (wear := car_wear(car)) is not None
    ]
    due = sum(needs_service(car) for car in fleet)

    return {
        "count": len(fleet),
        "due": due,
        "average_wear": mean(wear_values) if wear_values else 0.0,
    }

    



def print_report(fleet):
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))

    summary = fleet_summary(fleet)

    print("Fleet: %d cars" % summary["count"])
    print("Due for service: %d" % summary["due"])

    total_km = sum(car["odometer"] for car in fleet)
    total_miles = fleet_utils.km_to_miles(total_km)

    # The partner garage in England needs the distance in miles.
    print(
        "Fleet distance: %s miles"
        % fleet_utils.format_number(total_miles)
    )

    flush_log(get_setting(settings, "log_file", "km_wachter.log"))