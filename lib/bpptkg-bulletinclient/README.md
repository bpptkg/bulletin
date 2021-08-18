# bpptkg-bulletinclient

bpptkg-bulletinclient is a Python library primarily used to send WebObs update
signals to the BPPTKG bulletin web services.

## Installation

Install from PyPI by running this command:

    pip install -U bpptkg-bulletinclient

## Guides

You can see the guides by viewing command help:

    bulletinclient -h

## Failed Request Data

If bulletinclient failed to send the request, it will store the data (JSON
format) in the `~/.bulletin/failedrequest/` directory. You can use the data to
investigate the problem or send the data again to the bulletin web services.

## License

[MIT](https://github.com/bpptkg/bulletin/blob/main/LICENSE)
