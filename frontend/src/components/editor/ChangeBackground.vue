<script setup lang="ts">
import { apiPost } from "@/api/api";
import Swal from "sweetalert2";
import { inject, ref } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";

const props = defineProps<{
    scale: number | null;
}>();

const emit = defineEmits<{
    (e: "change-background", backgroundUrl: string): void;
    (e: "change-scale", scale: number): void;
}>();

const route = useRoute();
const mapPartId = inject(mapPartIdKey);
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

    await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/background`, {
        file: base64
    });

    emit("change-background", base64);
}

async function changeScale() {
    const res = await Swal.fire({
        title: "Ändra skala på bakgrunden",
        input: "text",
        showCancelButton: true,
        showLoaderOnConfirm: true,
        allowOutsideClick: () => !Swal.isLoading()
    });
    if (res.isConfirmed && res.value) {
        const scale = parseFloat(res.value);
        await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/background_scale`, {
            scale: scale
        });
        emit("change-scale", scale);
    }
}
</script>
<template>
    <div class="border p-1">
        <button class="btn btn-secondary m-2" @click="fileInput?.click()">Ändra bakgrundsbild</button>
        <input
            type="file"
            ref="fileInput"
            class="form-control hide"
            accept=".png,.svg,.jpg,.webp"
            @change="changeBackground"
        >
        <button class="btn btn-secondary m-2" @click="changeScale">Ändra skala</button>
        <span>Nuvarande skala på bakgrunden: {{ props.scale ?? "laddar..." }}</span>
    </div>
</template>

<style scoped>
.border {
    border: 1px solid #ddd;
    border-radius: 5px;
}
.hide {
    display: none;
}
</style>