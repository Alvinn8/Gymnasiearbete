<script setup lang="ts">
import { useHighlightedRoomCategory } from "@/stores/highlight";
import { usePanzoom } from "@/stores/panzoom";
import { useSelection } from "@/stores/selection";
import { computed, onMounted, ref, toRef, watch } from "vue";

const props = defineProps<{
    id: number;
    name: string | null;
    x: number;
    y: number;
    width: number;
    height: number;
    categoryId: number | null;
    counterRotationDeg: number;
}>();

const hovered = ref(false);
const selection = useSelection("room", toRef(props, "id"));
const highlightedRoomCategory = useHighlightedRoomCategory();
const highlighted = computed(() =>
    highlightedRoomCategory.roomCategoryId !== null && highlightedRoomCategory.roomCategoryId === props.categoryId
);

const divRef = ref<HTMLDivElement | null>(null);
const spanRef = ref<HTMLSpanElement | null>(null);
const panzoom = usePanzoom();

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
    }
}, { immediate: true });

onMounted(() => {
    if (!divRef.value || !spanRef.value) return;
    
    const divBox = divRef.value.getBoundingClientRect();
    let spanBox = spanRef.value.getBoundingClientRect();

    let fontSize = 25;
    while ((spanBox.width > divBox.width || spanBox.height > divBox.height) && fontSize > 1) {
        // The text is too big, we need to make it smaller.
        fontSize -= 5;
        if (fontSize <= 0) {
            fontSize = 1;
        }
        spanRef.value.style.fontSize = fontSize + "px";
        if (fontSize <= 10) {
            spanRef.value.style.padding = "1px";
            spanRef.value.style.borderRadius = "3px";
        }
        spanBox = spanRef.value.getBoundingClientRect();
    }
});

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        ref="divRef"
        :class="{
            selected: selection.selected.value,
            hovered: hovered,
            highlighted: highlighted
        }"
        @mouseover="() => hovered = true"
        @mouseout="() => hovered = false"
        @click="selection.select()"
        @touchend="selection.select()"
    >
        <span
            v-if="name"
            ref="spanRef"
            :style="{ transform: `rotate(${counterRotationDeg}deg)` }"
        >{{ name }}</span>
    </div>
</template>

<style scoped>
div {
    background-color: rgba(0, 0, 0, 0.15);
    position: absolute;
    z-index: 2;
    
    /* center text */
    display: flex;
    justify-content: center;
    align-items: center;
}
span {
    background-color: rgba(255, 255, 255, 0.5);
    color: black;
    padding: 3px;
    border-radius: 5px;
    font-size: 25px;
}
.hovered {
    background-color: rgba(0, 0, 0, 0.3);
}
.highlighted {
    background-color: rgba(0, 255, 0, 0.1);
}
.selected {
    background-color: rgba(0, 255, 0, 0.3);
}
</style>