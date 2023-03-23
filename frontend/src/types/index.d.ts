/**
 * A pair of position coordinates.
 */
export type Position = {
    x: number;
    y: number;
};

/**
 * Width and height.
 */
export type Size = {
    width: number;
    height: number;
};

/**
 * Something with a position and size.
 */
export type Dimensions = Position & Size;

export type DimensionsProperty = keyof Dimensions;

/**
 * Something that has an id.
 */
export type Identifiable = {
    id: number;
};

/**
 * A wall on a map.
 */
export type Wall = Identifiable & Dimensions;

/**
 * A point on a map.
 */
export type Point = Identifiable & Position;

/**
 * A connection between two points on a map.
 */
export type PointConnection = Identifiable & {
    point_a: Position;
    point_b: Position;
};

/**
 * Brief information about a point with only x, y and z.
 */
export type PointWithZ = Point & { z: number };

/**
 * A type for a map part.
 */
export type MapPart = {
    id: number;
    name: string;
    z: number;
    offsetX: number;
    offsetY: number;
    rotationDeg: number;
};

/**
 * A room.
 */
export type Room = Identifiable & Dimensions & {
    name: string | null;
    /**
     * The id of the point where this room has a door.
     */
    doorAtPointId: number;
    /**
     * The id of the category of the room.
     */
    categoryId?: number | null;
}

/**
 * A room with a z coordinate.
 */
export type RoomWithZ = Room & {
    z: number;
};

/**
 * A category of a room.
 */
export type RoomCategory = {
    id: number;
    name: string;
}

/**
 * A staircase on the map.
 */
export type Staircase = Dimensions & {
    id: number;
    mapPartId: number;
    /** The id of another staircase. */
    connectsTo: number | null;
};