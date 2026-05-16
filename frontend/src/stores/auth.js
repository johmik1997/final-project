import { defineStore } from "pinia";
import { ref } from "vue";

export const useAuth = defineStore("authStore", () => {
  const auth = ref();

  function setAuth(val) {
    auth.value = val;
  }

  return { auth, setAuth };
});
