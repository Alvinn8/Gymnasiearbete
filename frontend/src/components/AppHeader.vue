<script setup lang="ts">
import { RouterLink } from "vue-router";
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
      </nav>
    </div>
  </header>
</template>