<script setup lang="ts">
import { computed, ref } from "vue";
import { apiPost, handleNetworkError } from "@/api/api";
import { setAuthToken } from "@/api/auth";
import Swal from "sweetalert2";
import router from "@/router";

const username = ref<string>("");
const password = ref<string>("");
const loading = ref<boolean>(false);

const canSubmit = computed(() => {
    return !loading.value
        && username.value.length > 0
        && password.value.length > 0;
});

function submit() {
    loading.value = true;
    apiPost("login", {
        username: username.value,
        password: password.value
    }).then(json => {
        if (json.success) {
            const token = json.token;
            setAuthToken(token);
            router.push({
                name: "test"
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
        <h1>Logga in som kartskapare</h1>
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