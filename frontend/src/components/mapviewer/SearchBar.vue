<script setup lang="ts">
defineProps<{
    modelValue: string;
    showBackArrow: boolean;
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: string): void;
    (e: "focus"): void;
    (e: "blur"): void;
    (e: "back"): void;
}>();
</script>

<template>
    <div class="search-bar">
        <div class="back-arrow"
            v-if="showBackArrow"
            @click="emit('back')"
        >
            <!-- SVG From https://icons.getbootstrap.com/icons/arrow-left/ -->
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
            </svg>
        </div>
        <input
            type="text"
            placeholder="Sök"
            :value="modelValue"
            @input="(e) => emit('update:modelValue', (e.target as HTMLInputElement).value)"
            @focus="emit('focus')"
            @blur="emit('blur')"
        >
    </div>
</template>

<style scoped>
.back-arrow {
    display: inline-block;
    margin-right: 15px;
}
.search-bar {
    width: calc(100vw - 20px);
    height: 50px;
    margin: 10px;
    padding: 12px;
    padding-left: 20px;
    background: white;
    z-index: 10;
    position: fixed;
    left: 0px;
    top: 0px;
    border-radius: 10px;
    border: 1px solid #bbb;
    cursor: pointer;
    box-shadow: 2px 2px 4px 1px;
}
input {
    margin: 0;
    padding: 0;
    background: transparent;
    border: none;
    outline: none;
}
@media (min-width: 600px)  {
    .search-bar {
        max-width: 400px;
    }
}
</style>