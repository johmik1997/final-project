import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useCirculation = defineStore('circulationStore', () => {
  const circulations = ref([]);

  function getCirculationId(circ) {
    return circ?.id || circ?.circulationUuid || circ?.uuid;
  }

  function set(data) {
    circulations.value = data;
  }

  function getAll() {
    return circulations.value;
  }

  function add(data) {
    circulations.value.unshift(data);
  }

  function update(id, data) {
    const idx = circulations.value.findIndex((el) => getCirculationId(el) == id);
    if (idx === -1) return;
    circulations.value.splice(idx, 1, data);
  }

  function remove(id) {
    const idx = circulations.value.findIndex((el) => getCirculationId(el) == id);
    if (idx === -1) return;
    circulations.value.splice(idx, 1);
  }

  return {
    circulations,
    set,
    getAll,
    add,
    update,
    remove,
  };
});
