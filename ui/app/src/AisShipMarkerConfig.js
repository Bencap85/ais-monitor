import { NAVIGATIONAL_STATUS, NAVIGATIONAL_STATUS_TO_CODE, CODE_TO_NAVIGATIONAL_STATUS, SHIP_STATUSES } from "./constants/constants";
import { getStatus } from "./sidebar/AisShipsListItem";


const colors = {
    BLUE: "#008cffff",
    GREEN: "#11ff00ff",
    YELLOW: "#e5ff00ff",
    ORANGE: "#ff7700ff",
    RED: "#ff0000ff",
}

const darkColors = {
    DARK_BLUE: "#0063b4ff",
    DARK_GREEN: "#0a9500ff",
    DARK_YELLOW: "#a9bb00ff",
    DARK_ORANGE: "#aa4f00ff",
    DARK_RED: "#8e0000ff"
}

const COLOR_TO_DARK = {
    [colors.BLUE]: darkColors.DARK_BLUE, 
    [colors.GREEN]: darkColors.DARK_GREEN, 
    [colors.YELLOW]: darkColors.DARK_YELLOW, 
    [colors.ORANGE]: darkColors.DARK_ORANGE, 
    [colors.RED]: darkColors.DARK_RED, 
}

const shipTypeColors = {
  "Wing In Ground Craft": colors.GREEN,
  "Fishing": colors.GREEN,
  "Towing": colors.YELLOW,
  "Dredging/Underwater Ops": colors.ORANGE,
  "Diving Ops": colors.YELLOW,
  "Military ops": colors.RED,
  "Sailing": colors.GREEN,
  "Pleasure Craft": colors.GREEN,
  "High Speed Craft": colors.GREEN,
  "Pilot Vessel": colors.YELLOW,
  "Search and Rescue": colors.BLUE,
  "Tug": colors.YELLOW,
  "Port Tender": colors.YELLOW,
  "Anti-pollution": colors.GREEN,
  "Law enforcement vessel": colors.ORANGE,
  "Passenger Ship": colors.GREEN,
  "Cargo Ship": colors.BLUE,
  "Tanker": colors.BLUE,
  "Other Ship": colors.GREEN,
  "Medical Transport": colors.ORANGE,
  "Dangerous Goods": colors.RED,
  "Harmful Substances": colors.RED,
  "IMO Hazard": colors.RED,
  "Hazardous Cargo Unknown": colors.RED,
  "Other Special Category": colors.GREEN
};

export const MARKER_SHAPE = {
    CIRCLE: "circle",
    SHIP: "ship",
    SQUARE: "square"
}

export const NAVIGATIONAL_STATUS_TO_SHAPE = {
    [NAVIGATIONAL_STATUS.AT_ANCHOR]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.AGROUND]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.MOORED]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.NOT_UNDER_COMMAND]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.UNDER_WAY_USING_ENGINE]: MARKER_SHAPE.SHIP,
    [NAVIGATIONAL_STATUS.UNDER_WAY_SAILING]: MARKER_SHAPE.SHIP,
    [NAVIGATIONAL_STATUS.RESTRICTED_MANUVERABILITY]: MARKER_SHAPE.SHIP,
    [NAVIGATIONAL_STATUS.CONSTRAINED_BY_HER_DRAUGHT]: MARKER_SHAPE.SHIP,
};

export const NAVIGATIONAL_STATUS_CODE_TO_SHAPE = {
    [NAVIGATIONAL_STATUS.AT_ANCHOR]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.AGROUND]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.MOORED]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.NOT_UNDER_COMMAND]: MARKER_SHAPE.CIRCLE,
    [NAVIGATIONAL_STATUS.UNDER_WAY_USING_ENGINE]: MARKER_SHAPE.SHIP,
    [NAVIGATIONAL_STATUS.UNDER_WAY_SAILING]: MARKER_SHAPE.SHIP,
    [NAVIGATIONAL_STATUS.RESTRICTED_MANUVERABILITY]: MARKER_SHAPE.SHIP,
    [NAVIGATIONAL_STATUS.CONSTRAINED_BY_HER_DRAUGHT]: MARKER_SHAPE.SHIP,
};

export function getMarkerColor(ship) {
    const typeName = ship?.ShipTypeName || "Unknown";

    let color = "";
 
    if (!typeName) color = shipTypeColors["Other Ship"];
    else if (typeName.includes("Wing In Ground Craft")) color = shipTypeColors["Wing In Ground Craft"];
    else if (typeName.includes("Military ops")) color = shipTypeColors["Military ops"];
    else if (typeName.includes("High Speed Craft")) color = shipTypeColors["High Speed Craft"];
    else if (typeName.includes("Passenger ship")) color = shipTypeColors["Passenger Ship"];
    else if (typeName.includes("Cargo ship")) color = shipTypeColors["Cargo Ship"];
    else if (typeName.includes("Tanker")) color = shipTypeColors["Tanker"];
    else if (typeName.includes("Medical transport")) color = shipTypeColors["Medical Transport"];
    else if (typeName.includes("dangerous goods")) color = shipTypeColors["Dangerous Goods"];
    else if (typeName.includes("harmful substances")) color = shipTypeColors["Harmful Substances"];
    else if (typeName.includes("IMO hazard")) color = shipTypeColors["IMO Hazard"];
    else if (typeName.includes("hazardous cargo")) color = shipTypeColors["Hazardous Cargo Unknown"];
    else if (typeName.includes("Other special category")) color = shipTypeColors["Other Special Category"];
    else color = shipTypeColors[typeName] || shipTypeColors["Other Ship"];
    
    const status = getStatus(ship);
    if (status === SHIP_STATUSES.OFFLINE) {
        color = COLOR_TO_DARK[color];
    }

    return color;

}

export function getMarkerShape(ship) {
    if (ship.TrueHeading === 511) return MARKER_SHAPE.SQUARE;

    const navigationalStatus = CODE_TO_NAVIGATIONAL_STATUS[ship.NavigationalStatus] || "Unknown";
    return NAVIGATIONAL_STATUS_TO_SHAPE[navigationalStatus] || MARKER_SHAPE.SHIP;
}
