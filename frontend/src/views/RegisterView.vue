<script setup lang="ts">
import { computed, ref } from "vue";
import { apiPost, handleNetworkError } from "@/api/api";
import Swal from "sweetalert2";

const username = ref<string>("");
const password = ref<string>("");
const confirmPassword = ref<string>("");
const loading = ref<boolean>(false);

const canSubmit = computed(() => {
    return !loading.value
        && username.value.length > 0
        && password.value.length > 0
        && confirmPassword.value.length > 0;
});

function submit() {
    if (password.value != confirmPassword.value) {
        Swal.fire({
            title: "Felaktigt bekräftat lösenord",
            text: "Det bekräftade lösenordet överensstämmer inte med lösenordet.",
            icon: "error"
        });
        return;
    }

    loading.value = true;
    apiPost("register", {
        username: username.value,
        password: password.value
    }).then(json => {
        if (json.success) {
            Swal.fire({
                title: "Kontot har skapats",
                icon: "success"
            });
        } else {
            Swal.fire({
                title: json.error,
                icon: "error"
            });
        }
        loading.value = false;
    }).catch(() => {
        handleNetworkError();
        loading.value = false;
    });
    
}

</script>

<template>
    <div class="container">
        <h1>Skapa konto som kartskapare</h1>
        <p>Som kartskapare kan du skapa och redigera kartor.</p>
        <div class="mb-3">
            <label for="username" class="form-label">Användarnamn</label>
            <input type="text" v-model="username" class="form-control" id="username">
        </div>
        <div class="mb-3">
            <label for="password" class="form-label">Lösenord</label>
            <input type="password" v-model="password" class="form-control" id="password">
        </div>
        <div class="mb-3">
            <label for="confirm-password" class="form-label">Bekräfta lösenordet</label>
            <input type="password" v-model="confirmPassword" class="form-control" id="confirm-password">
        </div>
        <button @click="submit" :disabled="!canSubmit" class="btn btn-success">Skapa konto</button>
    </div>
</template>

<style scoped>
.container {
    max-width: 600px;
}
</style>