import os
from dotenv import load_dotenv
from weather import get_weather_info
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

    weather_info = get_weather_info(home_latitude, home_longitude)
    message_body = format_message(weather_info)
    send_mms(sender_email, sender_password, recipient_email, message_body)


if __name__ == "__main__":
    main()
