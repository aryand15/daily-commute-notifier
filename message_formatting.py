"""Module that handles converting structured commute info into human-digestible content."""

from transit import BusArrivalInfo
from weather import WeatherInfo


def format_message(
    weather_info: WeatherInfo,
    bus_arrival_info: BusArrivalInfo | None
) -> str:
    """
    Convert commute info into an SMS-friendly briefing.

    Args:
        weather_info (WeatherInfo): Structured weather information.
        bus_arrival_info (BusArrivalInfo | None): Structured bus arrival info, or None if no arrival is available.

    Returns:
        str: Formatted commute briefing.
    """

    umbrella_text = (
        "should bring an umbrella"
        if weather_info["umbrella_needed"]
        else "do not need to bring an umbrella"
    )

    lines = [
        (
            f"It will be {weather_info['summary']} overall today, "
            f"with a low of {weather_info['low']}°F and "
            f"high of {weather_info['high']}°F. "
            f"You {umbrella_text}."
        ),
        ""
    ]

    if bus_arrival_info is None:
        lines.append("No upcoming bus arrivals found right now.")
    else:
        lines.append(f"Be prepared to reach the bus stop at {bus_arrival_info['arrival_time']}.")
        if bus_arrival_info["alerts"]:
            lines.append(f"Alerts: {', '.join(bus_arrival_info['alerts'])}")

    lines.extend(
        [
            "",
            "Morning commute:",
        ]
    )

    for point in weather_info["morning_commute"]:
        line = (
            f"{point['time']}: "
            f"{point['temperature']}°F | "
            f"{point['condition']}"
        )

        if point["rain_probability"] > 0:
            line += f" | rain {point['rain_probability']}%"

        lines.append(line)

    lines.extend(
        [
            "",
            "Evening commute:",
        ]
    )

    for point in weather_info["evening_commute"]:
        line = (
            f"{point['time']}: "
            f"{point['temperature']}°F | "
            f"{point['condition']}"
        )

        if point["rain_probability"] > 0:
            line += f" | rain {point['rain_probability']}%"

        lines.append(line)

    if weather_info["rain_times"]:
        lines.extend(
            [
                "",
                "Potential rain:",
                ", ".join(weather_info["rain_times"]),
            ]
        )

    return "\n".join(lines)
