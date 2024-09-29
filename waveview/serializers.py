import pandas as pd


def sanitize(event: dict) -> dict:
    column_names = [
        "eventid",
        "eventdate",
        "eventdate_microsecond",
        "number",
        "duration",
        "amplitude",
        "magnitude",
        "longitude",
        "latitude",
        "depth",
        "eventtype",
        "seiscompid",
        "valid",
        "projection",
        "operator",
        "timestamp",
        "timestamp_microsecond",
        "count_deles",
        "count_labuhan",
        "count_pasarbubar",
        "count_pusunglondon",
        "ml_deles",
        "ml_labuhan",
        "ml_pasarbubar",
        "ml_pusunglondon",
        "location_mode",
        "location_type",
    ]

    if isinstance(event, dict):
        df = pd.DataFrame([event])
    else:
        df = pd.DataFrame(event)

    df["eventdate"] = pd.to_datetime(df["eventdate"]).dt.strftime(
        "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime(
        "%Y-%m-%dT%H:%M:%S.%f%z"
    )

    df = df.astype(object).where((pd.notnull(df)), None)
    if df.empty:
        return {}

    return df[column_names].to_dict(orient="records")[0]
