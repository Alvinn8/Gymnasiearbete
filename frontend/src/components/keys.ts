import type { PanZoom } from "panzoom";
import type { InjectionKey, Ref } from "vue";

/**
 * A provide/inject key for the current map part id.
 */
export const mapPartIdKey = Symbol("mapPartId") as InjectionKey<Ref<number>>;

/**
 * A provide/inject key for the panzoom object.
 */
export const panzoomKey = Symbol("panzoom") as InjectionKey<Ref<PanZoom>>;