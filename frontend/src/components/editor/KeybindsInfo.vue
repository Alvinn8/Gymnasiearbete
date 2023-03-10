<script setup lang="ts">
import { useKeybindInfo } from "@/stores/keybindsInfo";

const keybindInfo = useKeybindInfo();

</script>

<template>
    <template v-if="keybindInfo.groups">
        <div
            class="keyboard_info_group"
            v-for="group of keybindInfo.groups"
            :key="group.id"
        >
            <code
                class="key"
                v-for="key of group.keys"
                :key="key"
            >{{ key }}</code>
            <span class="description">{{ group.description }}</span>
        </div>
    </template>
</template>

<style scoped>
.key {
    background-color: black;
    color: white;
    padding: 2px 3px;
    border-radius: 3px;
    margin: 2px;
}
.description {
    margin-left: 10px;
}
.keyboard_info_group {
    display: inline-block;
    margin: 0px 10px;
}
</style>