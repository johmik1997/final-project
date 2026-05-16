import { onMounted, provide, ref, watch } from "vue";

export function useTablePagination(responseLimit = 25) {
  const page = ref(0);
  const search = ref('');
  const totalPages = ref(1);
  const limit = ref(responseLimit);
  const maxPage = ref();

  const done = ref(false)

  function reset() {
    page.value = 0
    limit.value = responseLimit
    done.value = false
  }

  function next() {
    if(page.value < limit.value) {
      page.value++
    }
  }

  function prev() {
    if((page.value - 1 > 0)) {
      page.value++
    }
  }

  function setPage(num) {
    console.log(num)
    page.value = num
  }

  provide('page', page.value)
  provide('limit', limit.value)
  provide('totalPages', totalPages.value)
  provide('setPage', setPage)

  return {
    reset,
    search,
    page,
    limit,
    done,
    totalPages,
    maxPage,
    setPage,
    next,
    prev
  }
}
