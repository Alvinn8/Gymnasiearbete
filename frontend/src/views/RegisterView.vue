<script setup lang="ts">
import { computed, ref } from "vue";
import { apiGet, apiPost, errorHandler, handleError } from "@/api/api";
import Swal from "sweetalert2";
import router from "@/router";
import { getSuccessfulLoginPage } from "@/stores/auth";

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

async function submit() {
    if (password.value != confirmPassword.value) {
        Swal.fire({
            title: "Felaktigt bekräftat lösenord",
            text: "Det bekräftade lösenordet överensstämmer inte med lösenordet.",
            icon: "error"
        });
        return;
    }

    loading.value = true;
    await apiPost("register", {
        username: username.value,
        password: password.value
    }).then(() => {
        router.push(getSuccessfulLoginPage());
    }).catch(errorHandler([
        [json => !json.success, (json: any) => Swal.fire({
            title: json.error,
            icon: "error"
        })]
    ]));
    loading.value = false;
    
}

async function registerWithGoogle() {
    const result = await apiGet("register/google").catch(handleError);
    localStorage.setItem("mapmaker.ouath_token", result.state);
    const url = new URL(location.href);
    const returnUrl = url.searchParams.get("returnUrl");
    if (returnUrl) {
        localStorage.setItem("mapmaker.ouath_register_return_url", returnUrl);
    }
    location.href = result.redirect_url;
}

</script>

<template>
    <div class="container">
        <h1>Skapa konto</h1>
        <div class="mb-3">
            <button class="btn btn-primary" @click="registerWithGoogle">Skapa konto med Google</button>
        </div>
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