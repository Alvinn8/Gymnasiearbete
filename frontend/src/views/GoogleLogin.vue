<script setup lang="ts">
import { apiPost, errorHandler } from "@/api/api";
import router from "@/router";
import { useAuth, getSuccessfulLoginPage } from "@/stores/auth";
import Swal from "sweetalert2";
import { onMounted, ref } from "vue";

const invalid = ref(false);

onMounted(async () => {
    const url = new URL(location.href);
    const code = url.searchParams.get("code"); 
    const state = url.searchParams.get("state");
    if (!code || !state) {
        invalid.value = true;
        return;
    }
    const currentState = localStorage.getItem("mapmaker.ouath_token");
    if (currentState !== state) {
        invalid.value = true;
        return;
    }
    localStorage.removeItem("mapmaker.ouath_token");

    const action = state.startsWith("register-") ? "register" : "login";

    const json = await apiPost("login/google/callback", { code, action })
        .catch(errorHandler([
            [json => !json.success, (json: any) => Swal.fire({
                title: json.error,
                icon: "error"
            })]
        ]));

    if (json) {
        const token = json.token;
        const auth = useAuth();
        auth.authToken = token;
        await auth.validateAuthToken();
        const returnUrl = localStorage.getItem("mapmaker.ouath_register_return_url");
        localStorage.removeItem("mapmaker.ouath_register_return_url");
        router.push(getSuccessfulLoginPage(returnUrl));
    }
});
</script>

<template>
    <div class="container" v-if="invalid">
        <h1>Försök igen</h1>
        <p>Försök att logga med Google igen.</p>
    </div>
</template>