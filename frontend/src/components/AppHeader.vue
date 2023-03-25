<script setup lang="ts">
import router from "@/router";
import { useAuth } from "@/stores/auth";
import { RouterLink } from "vue-router";

const auth = useAuth();

function logOut() {
    auth.authToken = null;
    router.push({
        name: "login"
    });
}

function getRegisterUrl() {
    let url = "/register";
    const returnUrl = router.currentRoute.value.query.returnUrl;
    if (typeof returnUrl === "string") {
        url += "?returnUrl=" + encodeURIComponent(returnUrl);
    }
    return url;
}

</script>

<template>
    <header>
        <nav class="navbar bg-primary navbar-expand-sm" data-bs-theme="dark">
            <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navbar-content"
                aria-controls="navbar-content" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbar-content">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <RouterLink to="/" class="nav-link" active-class="active">Startsida</RouterLink>
                    </li>
                    <li class="nav-item" v-if="!auth.isLoggedIn">
                        <RouterLink :to="getRegisterUrl()" class="nav-link" active-class="active">Skapa konto</RouterLink>
                    </li>
                    <li class="nav-item" v-if="!auth.isLoggedIn">
                        <RouterLink to="/login" class="nav-link" active-class="active">Logga in</RouterLink>
                    </li>
                    <li class="nav-item" v-if="auth.isLoggedIn">
                        <RouterLink to="/mapmaker/maps" class="nav-link" active-class="active">Mina Kartor</RouterLink>
                    </li>
                    <li class="nav-item" v-if="auth.isLoggedIn">
                        <a @click.prevent="logOut" href="#" class="nav-link">Logga ut</a>
                    </li>
                </ul>
            </div>
        </nav>
    </header>
</template>