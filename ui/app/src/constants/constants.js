export const DATA_SOURCES = {
    SATELLITE: "Satellite Imagery",
    AIS: "AIS Feed"
}

export const SHIP_STATUSES = {
    OFFLINE: "Offline",
    ONLINE: "Online"
}

export const shipTypeToColor = {
    "Aircraft Carrier": "#ff691eff",
    "Military": "#ff3b3b",
    "Other Warship": "#ff3b3b",
    "Submarine": "#ff3b3b",

    "Cargo": "#0d76ffff",
    "Container Ship": "#0d76ffff",

    "Other Ship": "#75ff75",
    "Landing": "#75ff75",
}

export const PIPELINE_STAGES = {
    "PipelineStage.FETCHING": "Fetching",
    "PipelineStage.DETECTING": "Detecting",
    "PipelineStage.CLASSIFYING": "Classifying",
    "PipelineStage.COMPLETED": "Completed"
}

export const NAVIGATIONAL_STATUS = {
    UNDER_WAY_USING_ENGINE: "Under way using engine",
    AT_ANCHOR: "At anchor",
    NOT_UNDER_COMMAND: "Not under command",
    RESTRICTED_MANUVERABILITY: "Restricted maneuverability",
    CONSTRAINED_BY_HER_DRAUGHT: "Constrained by her draught",
    MOORED: "Moored",
    AGROUND: "Aground",
    ENGAGED_IN_FISHING: "Engaged in fishing",
    UNDER_WAY_SAILING: "Under way sailing"
}

export const CODE_TO_NAVIGATIONAL_STATUS = {
    0: NAVIGATIONAL_STATUS.UNDER_WAY_USING_ENGINE,
    1: NAVIGATIONAL_STATUS.AT_ANCHOR,
    2: NAVIGATIONAL_STATUS.NOT_UNDER_COMMAND,
    3: NAVIGATIONAL_STATUS.RESTRICTED_MANUVERABILITY,
    4: NAVIGATIONAL_STATUS.CONSTRAINED_BY_HER_DRAUGHT,
    5: NAVIGATIONAL_STATUS.MOORED,
    6: NAVIGATIONAL_STATUS.AGROUND,
    7: NAVIGATIONAL_STATUS.ENGAGED_IN_FISHING,
    8: NAVIGATIONAL_STATUS.UNDER_WAY_SAILING
}

export const NAVIGATIONAL_STATUS_TO_CODE = {
    [NAVIGATIONAL_STATUS.UNDER_WAY_USING_ENGINE]: 0,
    [NAVIGATIONAL_STATUS.AT_ANCHOR]: 1,
    [NAVIGATIONAL_STATUS.NOT_UNDER_COMMAND]: 2,
    [NAVIGATIONAL_STATUS.RESTRICTED_MANUVERABILITY]: 3,
    [NAVIGATIONAL_STATUS.CONSTRAINED_BY_HER_DRAUGHT]: 4,
    [NAVIGATIONAL_STATUS.MOORED]: 5,
    [NAVIGATIONAL_STATUS.AGROUND]: 6,
    [NAVIGATIONAL_STATUS.ENGAGED_IN_FISHING]: 7,
    [NAVIGATIONAL_STATUS.UNDER_WAY_SAILING]: 8
}
