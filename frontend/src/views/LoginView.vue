<script setup lang="ts">
import { computed, ref } from "vue";
import { apiGet, apiPost, errorHandler, handleError } from "@/api/api";
import { getSuccessfulLoginPage } from "@/api/auth";
import Swal from "sweetalert2";
import router from "@/router";
import { useAuth } from "@/stores/auth";

const username = ref<string>("");
const password = ref<string>("");
const loading = ref<boolean>(false);

const canSubmit = computed(() => {
    return !loading.value
        && username.value.length > 0
        && password.value.length > 0;
});

async function submit() {
    loading.value = true;
    const json = await apiPost("login", {
        username: username.value,
        password: password.value
    }).catch(errorHandler([
        [json => !json.success, (json: any) => Swal.fire({
            title: json.error,
            icon: "error"
        })]
    ]));
    loading.value = false;
    if (json) {
        const token = json.token;
        const auth = useAuth();
        auth.authToken = token;
        await auth.validateAuthToken();
        router.push(getSuccessfulLoginPage());
    }
}

async function loginWithGoogle() {
    const result = await apiGet("login/google").catch(handleError);
    localStorage.setItem("mapmaker.ouath_token", result.state);
    location.href = result.redirect_url;
}

</script>

<template>
    <div class="container">
        <h1>Logga in som kartskapare</h1>
        <div class="mb-3">
            <button class="btn btn-primary" @click="loginWithGoogle">Logga in med Google</button>
        </div>
        <div class="mb-3">
            <label for="username" class="form-label">Användarnamn</label>
            <input type="text" v-model="username" class="form-control" id="username">
        </div>
        <div class="mb-3">
            <label for="password" class="form-label">Lösenord</label>
            <input type="password" v-model="password" class="form-control" id="password">
        </div>
        <button @click="submit" :disabled="!canSubmit" class="btn btn-success">Logga in</button>
    </div>
</template>

<style scoped>
.container {
    max-width: 600px;
}
</style>