import { defineStore } from "pinia";
import { ref } from "vue";

export const useColorStore = defineStore("colorStore", () => {
  const color = ref(
    localStorage.getItem("userColor")
      ? JSON.parse(localStorage.getItem("userColor"))
      : ""
  );

  function set(data) {
    color.value = data;
    localStorage.setItem("userColor", JSON.stringify(color.value));
  }

  function getColor() {
    return color.value;
  }

  return {
    color,
    set,
    getColor,
  };
});
