import os
from datetime import time
from dotenv import load_dotenv

from weather import get_weather_info
from transit import get_bus_arrival_info
from message_formatting import format_message
from sms import send_mms


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def get_required_float_env(name: str) -> float:
    value = get_required_env(name)

    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be a number."
        ) from exc


def main():
    load_dotenv()

    sender_email = get_required_env("SENDER_EMAIL")
    sender_password = get_required_env("SENDER_PASSWORD")
    recipient_email = get_required_env("RECIPIENT_EMAIL")

    home_latitude = get_required_float_env("HOME_LATITUDE")
    home_longitude = get_required_float_env("HOME_LONGITUDE")

    mbta_route_id = get_required_env("MBTA_ROUTE_ID")
    mbta_stop_id = get_required_env("MBTA_STOP_ID")
    mbta_direction_id = get_required_env("MBTA_DIRECTION_ID")
    target_arrival_time = time(7, 40)
    arrival_buffer = 5

    weather_info = get_weather_info(home_latitude, home_longitude)
    bus_info = get_bus_arrival_info(
        mbta_route_id,
        mbta_stop_id,
        mbta_direction_id,
        target_arrival_time,
        arrival_buffer
    )

    message_body = format_message(weather_info, bus_info)
    send_mms(sender_email, sender_password, recipient_email, message_body)


if __name__ == "__main__":
    main()
