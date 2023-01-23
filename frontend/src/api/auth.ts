import router from "@/router";

/**
 * Get the page the user should end up at after a successful login.
 */
export function getSuccessfulLoginPage() {
    const returnUrl = router.currentRoute.value.query["returnUrl"];
    if (typeof returnUrl !== "string") {
        // No return url, default to maps
        return { name: "maps" };
    }
    // A return url, let's redirect there
    return {
        path: returnUrl
    };
}