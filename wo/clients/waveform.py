import logging

from obspy import UTCDateTime
from obspy.clients.arclink.client import Client as ArcLinkClient
from obspy.clients.seedlink.basic_client import Client as SeedLinkClient

from ..constants import SE_STATIONS, STATIONS
from ..settings import ARCLINK_HOST, ARCLINK_PORT, SEEDLINK_HOST, SEEDLINK_PORT

logger = logging.getLogger(__name__)

SEEDLINK_CLIENT = "seedlink"
ARCLINK_CLIENT = "arclink"

# Time offset to wait when server still filling the data for buffering. For
# example, waveform data may not available immediately in the ArcLink server, so
# we need to wait several minutes for this buffering processes.
TIME_BUFFER_OFFSET = 3600  # 1 hour


class WaveformClient(object):
    """
    Adapter class to fetch waveform data through SeedLink or ArcLink client.
    """

    def __init__(
        self,
        seedlink_host="localhost",
        seedlink_port=18000,
        arclink_host="localhost",
        arclink_port=18001,
        timeout=5,
        use_client=None,
    ):
        self.seedlink_host = seedlink_host
        self.seedlink_port = seedlink_port
        self.arclink_host = arclink_host
        self.arclink_port = arclink_port
        self.timeout = timeout
        self.use_client = use_client

    def get_waveforms_via_seedlink(
        self, network, station, location, channel, starttime, endtime
    ):
        """
        Fetch waveform data via SeedLink.
        """
        logger.debug("Using SeedLink client.")
        client = SeedLinkClient(
            self.seedlink_host, self.seedlink_port, timeout=self.timeout
        )
        stream = client.get_waveforms(
            network, station, location, channel, starttime, endtime
        )
        return stream

    def get_waveforms_via_arclink(
        self, network, station, location, channel, starttime, endtime
    ):
        """
        Fetch waveform data via ArcLink.
        """
        logger.debug("Using ArcLink client.")
        client = ArcLinkClient(
            "client@cendana15.com",
            host=self.arclink_host,
            port=self.arclink_port,
            timeout=self.timeout,
        )
        stream = client.get_waveforms(
            network, station, location, channel, starttime, endtime
        )
        return stream

    def get_waveforms(self, network, station, location, channel, starttime, endtime):
        """
        Fetch waveform on current time window. Client is determined
        automatically using endtime value. If difference between endtime and now
        less than time buffer offset, use SeedLink client. Otherwise, use
        ArcLink client.
        """
        if self.use_client is None:
            delta = endtime - UTCDateTime()
            if abs(delta) < TIME_BUFFER_OFFSET:
                return self.get_waveforms_via_seedlink(
                    network, station, location, channel, starttime, endtime
                )
            return self.get_waveforms_via_arclink(
                network, station, location, channel, starttime, endtime
            )
        elif self.use_client == SEEDLINK_CLIENT:
            return self.get_waveforms_via_seedlink(
                network, station, location, channel, starttime, endtime
            )
        elif self.use_client == ARCLINK_CLIENT:
            return self.get_waveforms_via_arclink(
                network, station, location, channel, starttime, endtime
            )
        else:
            raise ValueError("Unsupported client type.")


def get_waveforms(starttime, endtime):
    client = WaveformClient(
        seedlink_host=SEEDLINK_HOST,
        seedlink_port=SEEDLINK_PORT,
        arclink_host=ARCLINK_HOST,
        arclink_port=ARCLINK_PORT,
    )

    stream = None
    delta = UTCDateTime() - endtime

    logger.info("Time delta offset: %.2f s", delta)

    if abs(delta) < TIME_BUFFER_OFFSET:
        for sta in SE_STATIONS:
            network = sta["network"]
            station = sta["station"]
            location = sta["location"]
            channel = sta["channel"]

            try:
                logger.info(
                    "Fetching waveform data for station " "%s (fast mode)...", station
                )
                stream = client.get_waveforms_via_seedlink(
                    network, station, location, channel, starttime, endtime
                )

            except Exception as e:
                logger.error(e)

    else:
        for sta in STATIONS:
            network = sta["network"]
            station = sta["station"]
            location = sta["location"]
            channel = sta["channel"]

            try:
                logger.info("Fetching waveform data for station %s...", station)
                msd = client.get_waveforms_via_arclink(
                    network, station, location, channel, starttime, endtime
                )

                logger.debug("Stream: %s", msd)

                if stream is None:
                    stream = msd
                else:
                    for tr in msd:
                        stream.append(tr)
            except Exception as e:
                logger.error(e)

    if stream is None:
        return None

    stream.merge(method=1, fill_value="interpolate")
    return stream
