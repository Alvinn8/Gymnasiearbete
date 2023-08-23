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

const showAdvanced = ref(false);

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
        <button
            class="btn btn-sm btn-secondary"
            style="margin: auto; margin-top: 40px; display: block;"
            @click="showAdvanced = !showAdvanced"
        >
            <template v-if="showAdvanced">Stäng avancerad info</template>
            <template v-else>Visa avancerad info</template>
        </button>
        <div v-if="showAdvanced">
            <h3>Hur skapar jag länkar som navigerar från A till B?</h3>
            <p>
                Starta en navigering på sidan och välj start och slutdestination. Markera
                slutdestination och tryck "Skapa länk" (eller QR-kod). Säkerställ att
                "Till:" och "Från:" är korrekta och använd länken eller QR-koden.
            </p>
            <h3>Hur skapar jag länkar som hittar närmaste rum av en kategori?</h3>
            <p>
                Tryck på "hitta närmaste" på en viss kategori från sökresultaten som vanligt
                på sidan och när navigeringen är igång, tryck på "Skapa länk" (eller QR-kod).
                Säkerställ att "Från:" och "Till närmaste ..." är korrekta och använd länken
                eller QR-koden.
            </p>
            <h3>Vad händer om rumnamnet ändras?</h3>
            <p>
                Länken innehåller både rum-ID:t och rumnamnet. Om namnet ändras kommer gamla
                länkar fortfarande att fungera eftersom rum-ID:t används.
            </p>
            <h3>Skapa länkar från tredjepartsverktyg</h3>
            <p>Är du en programmerare som vill skapa egna länkar från tredjepartsverktyg?</p>
            <p>
                Rum refereras till via rumnamn och rum-ID
                (<code>&lt;rumnamn&gt;-&lt;rum-ID&gt;</code>), men båda dessa är valfrida.
            </p>
            <p>
                Om ditt tredjepartsverktyg inte känner till ID:t kan du bara enge rumnamnet,
                och så länge det endast finns ett rum med detta namn kommer det användas.
                Det går även bra att endast ange ID:t och inte rumnamnet.
            </p>
            <p>
                Om både ID och namn anges, men dessa inte stämmer överens kommer sidan försöka
                lista ut vad användaren menar. Om du inte känner till rum-ID:t är det bättre
                att bara ange rumnamnet och inte ID:t. Om du även anger ID:t kommer det fungera
                ändå förutsatt att ett rum med rätt namn hittas, men om det inte hittas kan
                länken ge oväntade resultat.
            </p>
            <p>
                Du kan öppna JavaScript-konsollen för att se debugmeddelanden som beskriver
                hur sidan försöker hitta rummet från länken.
            </p>
        </div>
    </div>
</template>