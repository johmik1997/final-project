import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useReservation = defineStore('reservationStore', () => {
  const reservations = ref([]);

  function getReservationId(reservation) {
    return reservation?.id || reservation?.reservationUuid || reservation?.uuid;
  }

  function set(data) {
    reservations.value = data;
  }

  function getAll() {
    return reservations.value;
  }

  function add(data) {
    reservations.value.push(data);
  }

  function update(id, data) {
    const idx = reservations.value.findIndex((el) => getReservationId(el) == id);
    if (idx === -1) return;
    reservations.value.splice(idx, 1, data);
  }

  function remove(id) {
    const idx = reservations.value.findIndex((el) => getReservationId(el) == id);
    if (idx === -1) return;
    reservations.value.splice(idx, 1);
  }

  return {
    reservations,
    set,
    getAll,
    add,
    update,
    remove,
  };
});
