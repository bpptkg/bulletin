DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Network and station definitions used to fetch waveform data.
STATIONS = [
    {
        "network": "VG",
        "station": "MEDEL",
        "location": "00",
        "channel": "*H*",
    },
    {
        "network": "VG",
        "station": "MELAB",
        "location": "00",
        "channel": "*H*",
    },
    {
        "network": "VG",
        "station": "MEPAS",
        "location": "00",
        "channel": "*H*",
    },
    {
        "network": "VG",
        "station": "MEPUS",
        "location": "00",
        "channel": "*H*",
    },
]

# Station configuration for fast SeedLink fetching.
SE_STATIONS = [
    {
        "network": "VG",
        "station": "ME*",
        "location": "00",
        "channel": "*H*",
    },
]
