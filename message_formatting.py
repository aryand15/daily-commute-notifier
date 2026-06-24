"""Module that handles converting structured commute info into human-digestible content."""

from weather import WeatherInfo


def format_message(weather_info: WeatherInfo) -> str:
    """
    Convert WeatherInfo into an SMS-friendly weather briefing.

    Args:
        weather_info (WeatherInfo): Structured weather information.

    Returns:
        str: Formatted weather briefing.
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
            f"high of {weather_info['high']}°F."
        ),
        f"You {umbrella_text}.",
        "",
        "Morning commute:",
    ]

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