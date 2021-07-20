# WebObs

This directory contains code patches to keep WebObs MC3 and BPPTKG seismic
bulletin database in sync.

## Instructions

- Install `bpptkg-bulletinclient` library that was used to send request to the
  bulletin web services. For example:

      pip install -U bpptkg-bulletinclient

  If your bulletin web services URL differ from the libary provided, you can
  override the value by adding `--url <bulletin_webobs_endpoint_url>` option in
  the command arguments. You can view default URL endpoint by viewing command
  help:

      bulletinclient -h

- Modify trigger scripts `update_trigger`, `hide_trigger`, `delete_trigger`
  according to your need. The default command options provided should be
  sufficient.

- Copy `update_trigger`, `hide_trigger`, `delete_trigger` to
  `{WEBOBS_ROOT}/CODE/shells/`. Example `WEBOBS_ROOT` directory is
  `/opt/webobs/` (default provided in the scripts).

- Add the following code to the end block of
  `{WEBOBS_ROOT}/CODE/cgi-bin/editMC3.pl` file. For example we use `WEBOBS_ROOT`
  to `/opt/webobs/`. You can also see the example in the `editMC3.pl` in the
  current directory.

```perl
# ============================== START BLOCK ===================================
# The following contains additional code to keep WebObs MC3 and BPPTKG
# seismic_bulletin database in sync. The code patch has to be added to the newly
# installed WebObs, or one when upgrading WebObs version.
#
# For more information, see the guide at: https://gitlab.com/bpptkg/bulletin
# ==============================================================================
my $event_type;
if ($delete == 0) {
    # One modify an event.
    system("/opt/webobs/CODE/shells/update_trigger", "$anneeEvnt-$moisEvnt-$jourEvnt $heureEvnt:$minEvnt:$secEvnt", 2, $idSC3, $operator, "$anneeEvnt-$moisEvnt" . "#" . (abs($id_evt_modif)), $typeEvnt);
}
elsif ($delete == 1) {
    # One hide or restore an event.
    if ($id_evt_modif == abs($id_evt_modif)) {
        # One hide an event.
        $event_type = "NULL";
    }
    else {
        # One restore an event.
        $event_type = $typeEvnt;
    }
    system("/opt/webobs/CODE/shells/hide_trigger", "$anneeEvnt-$moisEvnt" . "#" . (abs($id_evt_modif)), $event_type, $operator);
}
elsif ($delete == 2) {
    # One delete an event.
    system("/opt/webobs/CODE/shells/delete_trigger", "$anneeEvnt-$moisEvnt" . "#" . (abs($id_evt_modif)), $operator);
}
# ============================== END BLOCK =====================================
```

If you add synchronous code in the trigger scripts, it may block current
operation. It can make longer loading in web browser when operator try to pick
or modify an event.

## How It Works

In the simplest manner, bulletinclient will send modifying signal to the
bulletin web services when one of the trigger script executed. Processing was
done in the background (in the bulletin web server) and asynchronously. So, the
operator do not need to wait till the processing was done as usually it takes
about 1 minute to update an event.
