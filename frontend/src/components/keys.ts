import type { InjectionKey, Ref } from "vue";

/**
 * A provide/inject key for the current map part id.
 */
export const mapPartIdKey = Symbol("mapPartId") as InjectionKey<Ref<number>>;