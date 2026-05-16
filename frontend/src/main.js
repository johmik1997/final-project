import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import vRipple from "@/directives/vRipple";
import vFocus from "@/directives/vFocus";
import modal from "@customizer/modal-x";
import toast from "@/toast";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(modal);
app.use(toast);

app.directive("ripple", vRipple);
app.directive("focus", vFocus);
app.mount("#app");
