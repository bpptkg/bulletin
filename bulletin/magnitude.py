import richter


def get_station_info():
    stations = [
        {
            'station': 'MEDEL',
            'component': 'Z',
            'network': 'VG',
            'ml_field': 'ml_deles',
            'app_field': 'count_deles',
        },
        {
            'station': 'MELAB',
            'component': 'Z',
            'network': 'VG',
            'ml_field': 'ml_labuhan',
            'app_field': 'count_labuhan',
        },
        {
            'station': 'MEPAS',
            'component': 'Z',
            'network': 'VG',
            'ml_field': 'ml_pasarbubar',
            'app_field': 'count_pasarbubar',
        },
        {
            'station': 'MEPUS',
            'component': 'Z',
            'network': 'VG',
            'ml_field': 'ml_pusunglondon',
            'app_field': 'count_pasarbubar',
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
            )

            app = richter.compute_app(
                stream,
                station['station'],
                network=station['network'],
                component=station['component'],
            )

            results[station['ml_field']] = ml
            results[station['app_field']] = app
        else:
            results[station['ml_field']] = None
            results[station['app_field']] = None
    return results
