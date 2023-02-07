export interface Dimensions {
    x: number;
    y: number;
    width: number;
    height: number;
}

export type DimensionsProperty = keyof Dimensions;

export type Wall = {
    id: number;
} & Dimensions;