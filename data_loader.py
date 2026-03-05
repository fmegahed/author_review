import time
from io import StringIO

import httpx
import pandas as pd

from config import CSV_BASE_URL, CSV_CACHE_TTL, TRACKS, TRACK_FIELD_MAPPINGS

# In-memory cache: {key: (dataframe, timestamp)}
_cache: dict[str, tuple[pd.DataFrame, float]] = {}


def _cache_key(track: str, kind: str) -> str:
    return f"{track}_{kind}"


def _is_fresh(key: str) -> bool:
    if key not in _cache:
        return False
    _, ts = _cache[key]
    return (time.time() - ts) < CSV_CACHE_TTL


def _fetch_csv(filename: str) -> pd.DataFrame:
    url = f"{CSV_BASE_URL}/{filename}"
    resp = httpx.get(url, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    return pd.read_csv(StringIO(resp.text))


def get_metadata(track: str) -> pd.DataFrame:
    key = _cache_key(track, "metadata")
    if not _is_fresh(key):
        df = _fetch_csv(TRACKS[track]["metadata_csv"])
        _cache[key] = (df, time.time())
    return _cache[key][0]


def get_factsheet(track: str) -> pd.DataFrame:
    key = _cache_key(track, "factsheet")
    if not _is_fresh(key):
        df = _fetch_csv(TRACKS[track]["factsheet_csv"])
        _cache[key] = (df, time.time())
    return _cache[key][0]


def clear_cache():
    _cache.clear()


def find_author_papers(author_name: str) -> list[dict]:
    """Search all tracks for papers by this author.

    Returns list of dicts: {arxiv_id, title, track, submitted, authors}
    sorted newest-first.
    """
    results = []
    author_lower = author_name.strip().lower()

    for track_id, track_cfg in TRACKS.items():
        try:
            metadata = get_metadata(track_id)
            factsheet = get_factsheet(track_id)
        except Exception:
            continue

        # Only include papers that exist in both metadata and factsheet
        factsheet_ids = set(factsheet["id"].astype(str))

        for _, row in metadata.iterrows():
            paper_id = str(row.get("id", ""))
            if paper_id not in factsheet_ids:
                continue

            authors_raw = str(row.get("authors", ""))
            author_list = [a.strip() for a in authors_raw.split("|")]
            if any(author_lower == a.lower() for a in author_list):
                results.append({
                    "arxiv_id": paper_id,
                    "title": str(row.get("title", "Untitled")),
                    "track": track_id,
                    "submitted": str(row.get("submitted", "")),
                    "authors": ", ".join(author_list),
                })

    # Sort newest first
    results.sort(key=lambda x: x["submitted"], reverse=True)
    return results


def _format_list_sentence(field_label: str, items: list[str]) -> str:
    """Format a list of items as a natural-language sentence.

    e.g. _format_list_sentence("chart family", ["Multivariate", "Bayesian"])
    → "Our app captured multiple chart family values: Multivariate and Bayesian."
    """
    if not items:
        return f"Our app did not capture any {field_label} values."
    if len(items) == 1:
        return f"Our app captured the following {field_label}: {items[0]}."
    if len(items) == 2:
        return f"Our app captured multiple {field_label} values: {items[0]} and {items[1]}."
    joined = ", ".join(items[:-1]) + f", and {items[-1]}"
    return f"Our app captured multiple {field_label} values: {joined}."


def get_paper_factsheet_data(arxiv_id: str, track: str) -> dict | None:
    """Get combined metadata + factsheet data for a single paper.

    Returns dict with all columns merged, or None if not found.
    """
    try:
        metadata = get_metadata(track)
        factsheet = get_factsheet(track)
    except Exception:
        return None

    meta_row = metadata[metadata["id"].astype(str) == arxiv_id]
    fact_row = factsheet[factsheet["id"].astype(str) == arxiv_id]

    if meta_row.empty or fact_row.empty:
        return None

    meta_dict = meta_row.iloc[0].to_dict()
    fact_dict = fact_row.iloc[0].to_dict()

    # Merge, factsheet values take precedence for overlapping keys
    combined = {**meta_dict, **fact_dict}

    # Clean up pipe-delimited track fields into natural-language sentences
    field_mappings = TRACK_FIELD_MAPPINGS.get(track, {})
    for field_key, field_info in field_mappings.items():
        col = field_info["column"]
        label = field_info["label"].lower()
        raw = str(combined.get(col, ""))
        if "|" in raw:
            items = [v.strip() for v in raw.split("|") if v.strip()]
            combined[col] = _format_list_sentence(label, items)
        elif raw and raw != "nan":
            combined[col] = f"Our app captured the following {label}: {raw}."

    # Also clean common pipe-delimited fields
    for col in ["authors"]:
        raw = str(combined.get(col, ""))
        if "|" in raw:
            combined[col] = ", ".join(v.strip() for v in raw.split("|") if v.strip())

    return combined
