"""Module that handles fetching transit information."""

from util import fetch_with_retries, format_timestamp
import datetime as dt
from typing import List, TypedDict


class BusArrivalInfo(TypedDict):
    arrival_time: str
    alerts: List[str]


def get_bus_arrival_info(mbta_route_id: str, mbta_stop_id: str, mbta_direction_id: str, target_arrival_time: dt.time | None = None, arrival_buffer: int | None = None) -> BusArrivalInfo | None:
    """
    Get arrival time and alert information for specific MBTA bus stop.

    Args:
        mbta_route_id (str): The ID of the MBTA bus route.
        mbta_stop_id (str): The ID of the MBTA bus stop.
        mbta_direction_id (str): The direction of travel, must be "0" or "1".
        target_arrival_time (datetime.time | None): The desired time at which 
            the bus should arrive. Defaults to None, in which case earliest arrival is chosen.
        arrival_buffer (int | None): The acceptable margin of error, in minutes, 
            around the desired target arrival time. Defaults to None.
    
    Returns:
        BusArrivalInfo | None: A dictionary containing the human-readable arrival time string 
        and alerts list according to either the earliest-first policy or the 
        closest-before-target policy. Returns None if no matching arrivals are found.
        
    Raises:
        ValueError: If mbta_direction_id is not "0" or "1".
    """

    if mbta_direction_id not in ("0", "1"):
        raise ValueError("mbta_direction_id must be '0' or '1'")

    url = (
        "https://api-v3.mbta.com/predictions?"
        f"filter[route]={mbta_route_id}&filter[stop]={mbta_stop_id}&"
        f"filter[direction_id]={mbta_direction_id}&"
        f"fields[prediction]=arrival_time&route_type=3&"
        "include=alerts&sort=arrival_time"
    )

    data = fetch_with_retries(url)
    raw_arrivals_list = data["data"]

    # Clean up fields from API response
    parsed_arrivals = []
    for arrival in raw_arrivals_list:
        time_str = arrival["attributes"].get("arrival_time")

        # Make sure the predicted arrival is there
        if time_str is None:
            continue
        
        # Convert raw string into datetime object for binary search calculations
        arrival_dt = dt.datetime.fromisoformat(time_str)
        arrival_time = format_timestamp(arrival_dt)
        alert_ids = [alert["id"] for alert in arrival["relationships"]["alerts"]["data"]]
        
        parsed_arrivals.append({
            "datetime_obj": arrival_dt,
            "info": {
                "arrival_time": arrival_time,
                "alerts": alert_ids
            }
        })

    if not parsed_arrivals:
        return None 
    
    # Use earliest arrival time when target arrival time and buffer are missing
    if target_arrival_time is None or arrival_buffer is None:
        return parsed_arrivals[0]["info"]

    # Define the acceptable buffer boundaries
    tz = parsed_arrivals[0]["datetime_obj"].tzinfo
    target_arrival_dt = dt.datetime.combine(dt.date.today(), target_arrival_time, tzinfo=tz)
    buffer_delta = dt.timedelta(minutes=arrival_buffer)
    min_acceptable = target_arrival_dt - buffer_delta
    max_acceptable = target_arrival_dt + buffer_delta

    # Binary search to find the closest arrival time before or at the target
    best_match = None
    min_diff = dt.timedelta.max

    l, r = 0, len(parsed_arrivals) - 1
    while l <= r:
        mid = (l + r) // 2
        current_dt = parsed_arrivals[mid]["datetime_obj"]

        # Check if arrival falls within valid window
        if min_acceptable <= current_dt <= max_acceptable:
            diff = abs(current_dt - target_arrival_dt)
            
            # Prioritize the policy: pick the closest possible time to our target
            if diff < min_diff:
                min_diff = diff
                best_match = parsed_arrivals[mid]["info"]

        # Binary search direction adjustments
        if current_dt < target_arrival_dt:
            l = mid + 1
        else:
            r = mid - 1

    return best_match
