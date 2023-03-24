<script setup lang="ts">
import { usePanzoom } from "@/stores/panzoom";
import { useSelection } from "@/stores/selection";
import { ref, toRef, watch } from "vue";

const props = defineProps<{
    id: number;
    x: number;
    y: number;
    width: number;
    height: number;
    z: number;
    connectsTo: number | null;
    connectsToZ: number;
    deltaZ: number;
    rotationDeg: number;
}>();

const emit = defineEmits<{
    (e: "change-floor", floor: number): void;
}>();

const selection = useSelection("staircase", toRef(props, "id"));
const staircaseSelection = useSelection("staircase");
const panzoom = usePanzoom();
const divRef = ref<HTMLDivElement | null>(null);
const flash = ref(false);

watch([selection.selected, panzoom, divRef], () => {
    if (selection.selected.value && panzoom.value && divRef.value) {
        const box = divRef.value.getBoundingClientRect();
        const transform = panzoom.value.getTransform();
        const x = (box.x - transform.x) / transform.scale;
        const y = (box.y - transform.y) / transform.scale;
        const width = box.width / transform.scale;
        const height = box.height / transform.scale;
        const newX = window.innerWidth / 2 - (x + width / 2) * transform.scale;
        const newY = window.innerHeight / 2 - (y + height / 2) * transform.scale;
        panzoom.value.smoothMoveTo(newX, newY);
        setTimeout(() => {
            flash.value = true;
        }, 1000);
    }
}, { immediate: true });

watch(flash, () => {
    if (flash.value) {
        setTimeout(() => {
            flash.value = false;
        }, 1000);
    }
});

function click() {
    if (!props.connectsTo) return;
    staircaseSelection.select(props.connectsTo);
    emit("change-floor", props.connectsToZ);
}

</script>

<template>
    <div :style="{
            left: x + 'px',
            top: y + 'px',
            width: width + 'px',
            height: height + 'px',
            transform: `rotate(${rotationDeg}deg)`
        }"
        :class="{
            flash: flash,
            ['rotate' + rotationDeg]: true
        }"
        ref="divRef"
        @click="click"
        @touchend="click"
    >
        <span v-if="deltaZ > 0">UPP</span>
        <span v-if="deltaZ < 0">NED</span>
    </div>
</template>

<style scoped>
div {
    --rotation-deg: 0deg;
    /** Repeating lines */
    background: repeating-linear-gradient(var(--rotation-deg), white, white 8px, black 8px, black 10px);
    position: absolute;
    z-index: 2;
    border: 1px solid black;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 1;
}
.rotate0 {
    border-bottom-width: 0;
    border-top-width: 2px;
    --rotation-deg: 0deg;
}
.rotate90 {
    border-right-width: 0;
    border-left-width: 2px;
    --rotation-deg: 90deg;
}
.rotate180 {
    border-top-width: 0;
    border-bottom-width: 2px;
    --rotation-deg: 180deg;
}
.rotate270 {
    border-left-width: 0;
    border-right-width: 2px;
    --rotation-deg: 270deg;
}
span {
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 5px;
    font-size: 10px;
}
.flash {
    animation: flash 1s;
}
@keyframes flash {
    50% {
        opacity: 0;
    }
}
</style>