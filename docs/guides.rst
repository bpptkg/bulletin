======
Guides
======

For current version, we provide the following endpoint to send update signal to
the Bulletin web services: ::

    GET /api/v1/webobs/

To work with the endpoint, you can install our bpptkg-bulletinclient libary: ::

    pip install -U bpptkg-bulletinclient

You can view the source code in the ``lib/bpptkg-bulletinclient/`` directory.
Default endpoint provided in the libary is
``http://192.168.0.43:9056/api/v1/webobs/``.

If a request failed to send to the server, bulletinclient will store the failed
request data in the ``~/.bulletin/failedrequest/`` directory.

Currently, supported actions are as follows:

- **WEBOBS_UPDATE_EVENT**

Send WEBOBS_UPDATE_EVENT signal to our web services to update an event in the
seismic bulletin database and do necessary fields calculation, e.g. magnitude,
energy, etc. The calculation is done in the background. So, it won't block the
request.

Example command: ::

  bulletinclient WEBOBS_UPDATE_EVENT --eventdate "2021-07-15 08:25:16.40" --sc3id "://bpptkg2021nupjan" --operator IND --eventtype MP --eventid "2021-07#235"

Note that all date time in the request use UTC time zone.

For this action, required payload is ``--eventdate`` (include miliseconds part
if any). The web server will fetch the event using this meta data from WebObs
MC3 bulletin. You can also pass ``--sc3id``, ``--eventid``, ``--eventtype``, and
``--operator`` options. These meta data will help the web services find the
right event to update.

If one observer update an event, it has eventid already created, e.g.
``2021-07#3455``. But for picking a new event, eventid may still generated.
WebObs put default eventid in the form ``2021-07#0``. It is not an issue,
because the web services will find the right event automatically for you. Your
job is to make sure you send necessary meta data sufficient for us to find the
right event.

You can use ``webobs_patch/update_trigger`` script to integrate the script in
the WebObs server.

- **WEBOBS_HIDE_EVENT**

Send WEBOBS_HIDE_EVENT to our web services to hide an event in the database.

Example command: ::

  bulletinclient WEBOBS_HIDE_EVENT --eventid "2021-07#2553" --operator YUL

For hiding an event, required payload is ``--eventid``.

You can use ``webobs_patch/hide_trigger`` script to integrate the script in the
WebObs server.

- **WEBOBS_RESTORE_EVENT**

Send WEBOBS_RESTORE_EVENT to our web services to restore an event in the
database.

Example command: ::

  bulletinclient WEBOBS_RESTORE_EVENT --eventid "2021-07#425" --eventtype ROCKFALL --operator RWL

For this action, required payloads are ``--eventid`` and ``--eventtype``.

You can use ``webobs_patch/hide_trigger`` script to integrate the script in the
WebObs server.

- **WEBOBS_DELETE_EVENT**

Send WEBOBS_DELETE_EVENT to our web services to delete an event in the database.
The web server apply soft delete (hide the event) instead of actually delete the
event in the database to prevent data loss.

Example command: ::

  bulletinclient WEBOBS_DELETE_EVENT --eventid "2021-07#5534" --operator YUL

For this action, required payload is ``--eventid``.

You can use ``webobs_patch/delete_trigger`` script to integrate the script in
the WebObs server.
