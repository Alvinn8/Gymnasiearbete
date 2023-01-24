import { apiGet, errorHandler } from "@/api/api";
import { getSuccessfulLoginPage } from "@/api/auth";
import { useAuth } from "@/stores/auth";
import { createRouter, createWebHistory, type NavigationGuard } from "vue-router";

const requireLogin: NavigationGuard = function(to) {
    const auth = useAuth();
    if (!auth.isLoggedIn) {
        // Redirect to login
        return {
            name: "login",
            query: {
                returnUrl: to.path
            }
        };
    }
};

const verifyMapExists: NavigationGuard = function(to) {
    return new Promise((resolve) => {
        const mapId = to.params.map_id;
        apiGet(`map/${mapId}/info`)
            .then(() => resolve())
            .catch(errorHandler([
                [json => !json.success, () => resolve({
                    name: "NotFound"
                })]
            ]));
    });
};

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/about",
            name: "about",
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import("../views/AboutView.vue")
        },
        {
            path: "/test",
            name: "test",
            component: () => import("../views/TestView.vue"),
            beforeEnter: [requireLogin]
        },
        {
            path: "/404",
            name: "NotFound",
            component: () => import("../views/error/NotFound.vue")
        },
        {
            path: "/register",
            name: "register",
            component: () => import("../views/RegisterView.vue")
        },
        {
            path: "/login",
            name: "login",
            component: () => import("../views/LoginView.vue"),
            beforeEnter: () => {
                const auth = useAuth();
                if (auth.isLoggedIn) {
                    // The user is already logged in
                    return getSuccessfulLoginPage();
                }
            }
        },
        // {
        //     path: "/login/google/callback",
        //     beforeEnter: (from) => {
        //         console.log(from.fullPath);
        //     }
        // },
        {
            path: "/mapmaker/maps",
            name: "maps",
            component: () => import("../views/mapmaker/MapsView.vue"),
            beforeEnter: [requireLogin]
        },
        {
            path: "/mapmaker/maps/new",
            component: () => import("../views/mapmaker/NewMapView.vue"),
            beforeEnter: [requireLogin]
        },
        {
            path: "/mapmaker/map/:map_id",
            component: () => import("../views/mapmaker/MapEditor.vue"),
            name: "map",
            beforeEnter: [requireLogin, verifyMapExists]
        }
    ]
});

export default router;
