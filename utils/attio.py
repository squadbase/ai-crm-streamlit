import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv(".env")

attio_api_key = os.getenv("ATTIO_ACCESS_TOKEN")


def get_deals(
    filter_by: Optional[Dict] = None,
    sort_by: Optional[List[Dict]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict:
    """
    Fetch deals from Attio API with optional filtering and sorting.

    Args:
        filter_by (Optional[Dict]): Filter criteria for the deals
        sort_by (Optional[List[Dict]]): Sorting criteria for the deals
        limit (Optional[int]): Maximum number of records to return
        offset (Optional[int]): Number of records to skip

    Returns:
        Dict: Response from the Attio API containing deals data
    """
    url = "https://api.attio.com/v2/objects/deals/records/query"

    headers = {
        "Authorization": f"Bearer {attio_api_key}",
        "Content-Type": "application/json",
    }

    payload = {}
    if filter_by:
        payload["filter_by"] = filter_by
    if sort_by:
        payload["sort_by"] = sort_by
    if limit is not None:
        payload["limit"] = limit
    if offset is not None:
        payload["offset"] = offset

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["data"]


def get_notes(
    record_id: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict:
    """
    Fetch notes from Attio API, optionally filtered by record ID.

    Args:
        record_id (Optional[str]): Filter notes by specific record ID
        limit (Optional[int]): Maximum number of notes to return
        offset (Optional[int]): Number of notes to skip

    Returns:
        Dict: Response from the Attio API containing notes data
    """
    url = "https://api.attio.com/v2/notes"

    headers = {
        "Authorization": f"Bearer {attio_api_key}",
        "Content-Type": "application/json",
    }

    params = {}
    if record_id:
        params["record_id"] = record_id
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()["data"]


def get_companies(
    filter_by: Optional[Dict] = None,
    sort_by: Optional[List[Dict]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict:
    """
    Fetch companies from Attio API with optional filtering and sorting.

    Args:
        filter_by (Optional[Dict]): Filter criteria for the companies
        sort_by (Optional[List[Dict]]): Sorting criteria for the companies
        limit (Optional[int]): Maximum number of records to return
        offset (Optional[int]): Number of records to skip

    Returns:
        Dict: Response from the Attio API containing companies data
    """
    url = "https://api.attio.com/v2/objects/companies/records/query"

    headers = {
        "Authorization": f"Bearer {attio_api_key}",
        "Content-Type": "application/json",
    }

    payload = {}
    if filter_by:
        payload["filter_by"] = filter_by
    if sort_by:
        payload["sort_by"] = sort_by
    if limit is not None:
        payload["limit"] = limit
    if offset is not None:
        payload["offset"] = offset

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["data"]
