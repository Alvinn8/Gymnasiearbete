<script setup lang="ts">
import { apiPost } from "@/api/api";
import { ref } from "vue";
import { useRoute } from "vue-router";

const props = defineProps<{
    currentMapPartId: number
}>();

const emit = defineEmits<{
    (e: "change-background", backgroundUrl: string): void
}>();

const route = useRoute();
const fileInput = ref<HTMLInputElement | null>(null);

async function changeBackground() {
    if (!fileInput.value?.files) return;

    const file = fileInput.value?.files[0];
    if (!file) return;

    const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => {
            const url = reader.result;
            if (typeof url !== "string") {
                reject();
                return;
            }
            resolve(url);
        };
    });

    await apiPost(`map/${route.params.map_id}/part/${props.currentMapPartId}/background`, {
        file: base64
    });

    emit("change-background", base64);
}

</script>
<template>
    <p>Ändra bakgrundsbild.</p>
    <input
        type="file"
        ref="fileInput"
        class="form-control"
        accept=".png,.svg,.jpg,.webp"
        @change="changeBackground"
    >
</template>