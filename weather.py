"""Module that handles fetching weather information."""

from __future__ import annotations
from datetime import datetime
from typing import List, TypedDict
from util import fetch_with_retries, format_hour


class WeatherDataPoint(TypedDict):
    time: str
    temperature: float
    condition: str
    rain_probability: int

class WeatherInfo(TypedDict):
    low: float
    high: float
    umbrella_needed: bool
    rain_times: List[str]
    morning_commute: List[WeatherDataPoint]
    evening_commute: List[WeatherDataPoint]


def interpret_weather_code(code: int) -> str:
    """
    Convert Open-Meteo weather codes into human-readable conditions.

    Args:
        code (int): WMO weather code.

    Returns:
        str: Human-readable weather condition.
    """
    if code == 0:
        return "Clear"
    if code in (1, 2):
        return "Partly Cloudy"
    if code == 3:
        return "Cloudy"
    if code in (45, 48):
        return "Fog"
    if code in (51, 53, 55):
        return "Drizzle"
    if code in (56, 57):
        return "Freezing Drizzle"
    if code in (61, 63, 65, 80, 81, 82):
        return "Rain"
    if code in (66, 67):
        return "Freezing Rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "Snow"
    if code in (95, 96, 99):
        return "Thunderstorm"

    return "Unknown"


def get_weather_info(
    lat: float,
    lng: float,
    umbrella_threshold: int = 40,
) -> WeatherInfo:
    """
    Generate a summary of the weather from 7:00 AM to 6:00 PM, focusing on key commuting time, using Open-Meteo.

    Important: this function assumes the notification is delivered before 7:00 AM, because it only returns forecasted weather data.
    So if it runs late, there will be a discrepancy between the returned forecast data and the real recorded data for hours between 7:00 AM and the delivery time of the notification.

    This function fetches:
        - Daily weather summary
        - Daily low/high temperatures
        - Umbrella recommendation (based on whether rain probability ever passes a threshold for any hour from 7:00 AM - 6:00 PM)
        - Morning commute forecast (temp, condition, and rain probability for each hour from 7:00 AM - 9:00 AM)
        - Evening commute forecast (temp, condition, and rain probability for each hour from 5:00 PM - 6:00 PM)
        - Predicted rain times (any hour from 7:00 AM - 6:00 PM)

    Args:
        lat (float): Latitude (-90 to 90).
        lng (float): Longitude (-180 to 180).
        umbrella_threshold (int): Rain probability percentage above which
            rain is considered likely.

    Returns:
        WeatherInfo: Structured weather information.

    Raises:
        ValueError: If coordinates are invalid.
        RuntimeError: If the API request repeatedly fails.
        KeyError: If expected forecast data is missing.
    """
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90.")

    if not (-180 <= lng <= 180):
        raise ValueError("Longitude must be between -180 and 180.")

    if not (0 <= umbrella_threshold <= 100):
        raise ValueError(
            "umbrella_threshold must be between 0 and 100."
        )

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lng}"
        "&hourly="
        "temperature_2m,precipitation_probability,weather_code"
        "&daily="
        "temperature_2m_max,"
        "temperature_2m_min,"
        "weather_code"
        "&temperature_unit=fahrenheit"
        "&forecast_days=1"
        "&timezone=auto"
    )

    data = fetch_with_retries(url)

    hourly = data["hourly"] 
    daily = data["daily"]

    timestamps: List[str] = hourly["time"]
    temperatures: List[float] = hourly["temperature_2m"]
    rain_probs: List[float] = hourly["precipitation_probability"]
    weather_codes: List[int] = hourly["weather_code"]

    forecast_lookup = {
        timestamp: {
            "temperature": temperature,
            "rain_probability": rain_probability,
            "condition": interpret_weather_code(weather_code),
        }
        for (
            timestamp,
            temperature,
            rain_probability,
            weather_code,
        ) in zip(
            timestamps,
            temperatures,
            rain_probs,
            weather_codes,
        )
    }

    forecast_date = timestamps[0][:10]

    def build_commute_point(
        display_time: str,
        forecast_time: str,
    ) -> WeatherDataPoint:
        timestamp = f"{forecast_date}T{forecast_time}"

        forecast = forecast_lookup[timestamp]

        return {
            "time": display_time,
            "temperature": round(forecast["temperature"]),
            "condition": forecast["condition"],
            "rain_probability": forecast["rain_probability"],
        }

    morning_commute = [
        build_commute_point("7:00 AM", "07:00"),
        build_commute_point("8:00 AM", "08:00"),
        build_commute_point("9:00 AM", "09:00"),
    ]

    evening_commute = [
        build_commute_point("5:00 PM", "17:00"),
        build_commute_point("6:00 PM", "18:00"),
    ]

    rain_times: List[str] = []

    for (
        timestamp,
        rain_probability,
    ) in zip(
        timestamps,
        rain_probs,
    ):
        dt = datetime.fromisoformat(timestamp)
        if dt.hour < 6 or dt.hour > 18:
            continue
        if rain_probability < umbrella_threshold:
            continue

        rain_times.append(format_hour(dt))

    # Pretty conservative but it's good to be prepared
    umbrella_needed = len(rain_times) > 0

    return {
        "summary": interpret_weather_code(
            daily["weather_code"][0]
        ),
        "low": round(daily["temperature_2m_min"][0]),
        "high": round(daily["temperature_2m_max"][0]),
        "umbrella_needed": umbrella_needed,
        "rain_times": rain_times,
        "morning_commute": morning_commute,
        "evening_commute": evening_commute,
    }
