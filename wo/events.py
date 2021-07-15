import enum


class BulletinEvent(enum.Enum):
    """
    Earthquake bulletin event types.

    Reference:
    https://bma.cendana15.com/docs/apis/monitoring/bulletin.html#event-code-reference
    """
    ANTHROP = 'ANTHROP'
    AUTO = 'AUTO'
    AWANPANAS = 'AWANPANAS'
    EXPLOSION = 'EXPLOSION'
    GASBURST = 'GASBURST'
    LAHAR = 'LAHAR'
    LF = 'LF'
    MP = 'MP'
    ROCKFALL = 'ROCKFALL'
    SOUND = 'SOUND'
    TECLOC = 'TECLOC'
    TECT = 'TECT'
    TELE = 'TELE'
    TPHASE = 'TPHASE'
    TREMOR = 'TREMOR'
    UNKNOWN = 'UNKNOWN'
    VTA = 'VTA'
    VTB = 'VTB'

    ALL = [
        ANTHROP,
        AUTO,
        AWANPANAS,
        EXPLOSION,
        GASBURST,
        LAHAR,
        LF,
        MP,
        ROCKFALL,
        SOUND,
        TECLOC,
        TECT,
        TELE,
        TPHASE,
        TREMOR,
        UNKNOWN,
        VTA,
        VTB,
    ]
