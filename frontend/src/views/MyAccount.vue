<script setup lang="ts">
import { apiGet, apiPost, errorHandler, handleError } from "@/api/api";
import Swal from "sweetalert2";
import { ref, watch } from "vue";

interface AccountDetails {
    username: string;
    has_password: boolean;
}

const accountDetails = ref<AccountDetails | null>(null);
const editedUsername = ref("");
const newPassword = ref<string | null>(null);
const confirmNewPassword = ref<string | null>(null);

apiGet("account/details")
    .then(info => accountDetails.value = info)
    .catch(handleError);

function changeUsername() {
    apiPost("account/change_username", {
        username: editedUsername.value
    }).then(() => {
        accountDetails.value!.username = editedUsername.value;
        editedUsername.value = "";
    }).catch(errorHandler([
        [json => !json.success, (json: any) => Swal.fire({
            icon: "error",
            text: json.error
        })]
    ]));
}

function changePassword() {
    newPassword.value = "";
    confirmNewPassword.value = "";
}

function saveNewPassword() {
    if (newPassword.value !== confirmNewPassword.value) {
        Swal.fire({
            icon: "error",
            text: "Fel upprepade lösenord"
        });
        return;
    }
    if (!newPassword.value || newPassword.value?.length === 0) {
        Swal.fire({
            icon: "error",
            text: "Ditt lösenord kan inte vara tomt"
        });
        return;
    }
    apiPost("account/change_password", {
        password: newPassword.value
    }).then(() =>
        Swal.fire({
            icon: "success",
            text: "Lösenordet har ändrats"
        }))
        .catch(handleError);

    newPassword.value = null;
    confirmNewPassword.value = null;
}

</script>

<template>
    <div class="container" style="max-width: 400px">
        <h1>Konto</h1>
        <div class="my-3">
            <h2>Användarnamn</h2>
            <div class="settings-entry">
                <template v-if="editedUsername">
                    <input type="text" class="form-control" v-model="editedUsername" autofocus>
                    <button class="btn btn-secondary" @click="editedUsername = ''">Avbryt</button>
                    <button class="btn btn-primary" @click="changeUsername">Spara</button>
                </template>
                <template v-else-if="accountDetails">
                    <span>{{ accountDetails.username }}</span>
                    <button class="btn btn-secondary" @click="editedUsername = accountDetails.username">Ändra</button>
                </template>
            </div>
            <h2>Lösenord</h2>
            <p v-if="!accountDetails?.has_password">
                Du har inget lösenord eftersom du loggade in med Google.
                Genom att skapa ett lösenord kan du även logga in med ditt användarnamn och lösenord.
            </p>
            <div v-if="newPassword !== null" class="settings-entry flex-column">
                <div class="d-flex password-entry">
                    <input type="password" class="form-control" v-model="newPassword" autofocus placeholder="Nytt lösenord">
                    <button class="btn btn-secondary" @click="newPassword = null">Avbryt</button>
                </div>
                <div class="d-flex password-entry">
                    <input type="password" class="form-control" v-model="confirmNewPassword" autofocus placeholder="Upprepa nytt lösenord">
                    <button class="btn btn-primary" @click="saveNewPassword">Spara</button>
                </div>
            </div>
            <button v-else class="btn btn-secondary" @click="changePassword">
                <template v-if="accountDetails?.has_password">Ändra lösenord</template>
                <template v-else>Skapa lösenord</template>
            </button>
        </div>
    </div>
</template>

<style scoped>
.settings-entry {
    display: flex;
    border-top: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
    padding: 8px 0px;
    gap: 5px;
}
.password-entry {
    gap: 5px;
}
.password-entry button {
    min-width: 73px;
}
.settings-entry span {
    display: flex;
    align-items: center;
}
.settings-entry button {
    margin-left: auto;
}
</style>