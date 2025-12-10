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

export const NAVIGATIONAL_STATUSES = {
    0: "Under way using engine",
    1: "At anchor",
    2: "Not under command",
    3: "Restricted maneuverability",
    4: "Constrained by her draught",
    5: "Moored",
    6: "Aground",
    7: "Engaged in fishing",
    8: "Under way sailing"
}