
# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service, interval):
    if interval <= 0:
        raise ValueError("Service interval must be positive")

    return max(0.0, km_since_service / interval * 100)


def needs_service(car):
    last = car.get("last_service_km")

    # Missing service history should not trigger a warning.
    if last is None:
        return False

    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)

    return pct >= WARN_AT_PERCENT


def check_fleet(fleet):
    flagged = []

    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print("SERVICE DUE: %s" % car["id"])

    return flagged
