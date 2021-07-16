import enum


class WebObsAction(enum.Enum):
    WEBOBS_UPDATE_EVENT = 1
    WEBOBS_HIDE_EVENT = 2
    WEBOBS_RESTORE_EVENT = 3
    WEBOBS_DELETE_EVENT = 4


SUPPORTED_WEBOBS_ACTION_NAMES = {
    WebObsAction.WEBOBS_UPDATE_EVENT.name,
    WebObsAction.WEBOBS_HIDE_EVENT.name,
    WebObsAction.WEBOBS_RESTORE_EVENT.name,
    WebObsAction.WEBOBS_DELETE_EVENT.name,
}

SUPPORTED_WEBOBS_ACTION_VALUES = {
    WebObsAction.WEBOBS_UPDATE_EVENT.value,
    WebObsAction.WEBOBS_HIDE_EVENT.value,
    WebObsAction.WEBOBS_RESTORE_EVENT.value,
    WebObsAction.WEBOBS_DELETE_EVENT.value,
}
