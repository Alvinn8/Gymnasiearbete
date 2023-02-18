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

export type MapPart = {
    id: number;
    name: string;
    z: number;
    offsetX: number;
    offsetY: number;
};