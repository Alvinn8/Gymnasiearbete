<script setup lang="ts">
import Swal from "sweetalert2";
import { defineAsyncComponent, onMounted, ref } from "vue";

const QrCode = defineAsyncComponent({
    loader: () => import("qrcode.vue")
});

export type LinkPopupData = {
    linkUrl: string;
    useQrCode: boolean;
    room?: {
        name: string;
    }
    pathfinding?: {
        from: string;
        to: string;
    }
    findingClosest?: {
        from: string;
        toCategory: string;
    }
};

defineProps<LinkPopupData>();

const emit = defineEmits<{
    (e: "close"): void;
}>();

const el = ref<HTMLDivElement>();

onMounted(() => {
    Swal.fire({
        icon: "info",
        didOpen(element) {
            element.appendChild(el.value!);
        },
        didClose() {
            emit("close");
        }
    });
});

</script>

<template>
    <div ref="el" class="text-center mt-3">
        <template v-if="room">
            Här är en {{ useQrCode ? 'QR-kod' : 'länk' }} till {{ room.name }}:<br>
        </template>
        <template v-else-if="pathfinding">
            Från: {{ pathfinding.from }}<br>
            Till: {{ pathfinding.to }}<br>
            {{ useQrCode ? 'QR-kod' : 'Länk' }}:
        </template>
        <template v-else-if="findingClosest">
            Från: {{ findingClosest.from }}<br>
            Till närmaste {{ findingClosest.toCategory }}<br> 
            {{ useQrCode ? 'QR-kod' : 'Länk' }}:
        </template>
        <template v-if="!useQrCode">
            <code style="user-select: all;">{{ linkUrl }}</code>
        </template>
        <div v-else class="mt-3">
            <QrCode :value="linkUrl" :size="300" />
        </div>
    </div>
</template>