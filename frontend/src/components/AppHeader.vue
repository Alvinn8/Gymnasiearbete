<script setup lang="ts">
import { removeAuthToken } from "@/api/auth";
import router from "@/router";
import { RouterLink } from "vue-router";

function logOut() {
  removeAuthToken();
  router.push({
    name: "login"
  });
}
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">
          <button class="btn btn-info">Home</button>
        </RouterLink>
        <RouterLink to="/about">
          <button class="btn btn-info">About</button>
        </RouterLink>
        <RouterLink to="/test">
          <button class="btn btn-info">Test</button>
        </RouterLink>
        <RouterLink to="/register">
          <button class="btn btn-info">Skapa konto</button>
        </RouterLink>
        <RouterLink to="/login">
          <button class="btn btn-info">Logga in</button>
        </RouterLink>
        <button class="btn btn-info" @click="logOut">Logga ut</button>
      </nav>
    </div>
  </header>
</template>