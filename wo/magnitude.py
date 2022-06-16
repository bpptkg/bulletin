import richter


def get_station_info():
    stations = [
        {
            'network': 'VG',
            'station': 'MEDEL',
            'channel': 'HHZ',
            'component': 'Z',
            'ml_field': 'ml_deles',
            'app_field': 'count_deles',
        },
        {
            'network': 'VG',
            'station': 'MELAB',
            'channel': 'HHZ',
            'component': 'Z',
            'ml_field': 'ml_labuhan',
            'app_field': 'count_labuhan',
        },
        {
            'network': 'VG',
            'station': 'MEPAS',
            'channel': 'HHZ',
            'component': 'Z',
            'ml_field': 'ml_pasarbubar',
            'app_field': 'count_pasarbubar',
        },
        {
            'network': 'VG',
            'station': 'MEPUS',
            'channel': 'EHZ',
            'component': 'Z',
            'ml_field': 'ml_pusunglondon',
            'app_field': 'count_pusunglondon',
        },
    ]
    return stations


def compute_magnitude_all(stream):
    """
    Calculate magnitude and amplitude peak-to-peak (app) for station MEDEL,
    MELAB, MEPAS, and MEPUS using bpptkg-richter library.

    Reference: https://github.com/bpptkg/bpptkg-richter
    """
    results = {}
    stations = get_station_info()

    for station in stations:
        if stream is not None:
            ml = richter.compute_ml(
                stream,
                station['station'],
                network=station['network'],
                component=station['component'],
                channel=station['channel'],
            )

            app = richter.compute_app(
                stream,
                station['station'],
                network=station['network'],
                component=station['component'],
                channel=station['channel'],
            )

            results[station['ml_field']] = ml
            results[station['app_field']] = app
        else:
            results[station['ml_field']] = None
            results[station['app_field']] = None
    return results
