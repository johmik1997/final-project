import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useBorrow = defineStore('borrowStore', () => {
  const borrows = ref([]);

  function getBorrowId(borrow) {
    return borrow?.id || borrow?.borrowUuid || borrow?.uuid;
  }

  function set(data) {
    borrows.value = data;
  }

  function getAll() {
    return borrows.value;
  }

  function add(data) {
    borrows.value.push(data);
  }

  function update(id, data) {
    const idx = borrows.value.findIndex((el) => getBorrowId(el) == id);
    if (idx === -1) return;
    borrows.value.splice(idx, 1, data);
  }

  function remove(id) {
    const idx = borrows.value.findIndex((el) => getBorrowId(el) == id);
    if (idx === -1) return;
    borrows.value.splice(idx, 1);
  }

  return {
    borrows,
    set,
    getAll,
    add,
    update,
    remove,
  };
});
