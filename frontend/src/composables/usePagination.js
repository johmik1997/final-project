import { computed, provide, ref, watch } from "vue";
import { useTablePagination } from "./useTablePagination";
import { useApiRequest } from "./useApiRequest";

export function usePagination(options = {}) {
  const paginationOptions = ref({
    cb: (f) => f,
    store: null,
    auto: true,
    perPage: 25,
    cache: false,
    ...(options || {}),
  });

  const search = ref("");
  const perPage = ref(paginationOptions.value.perPage);

  const req = useApiRequest();

  const searching = ref(false);
  const searchPagination = useTablePagination(perPage.value);
  const pagination = useTablePagination(perPage.value);

  function getPaginationData(next = true, current = false) {
    if (searching.value) {
      return JSON.parse(
        JSON.stringify({
          searchKey: search.value || undefined,
          search: search.value || undefined,
          page: next
            ? !current
              ? ++searchPagination.page.value
              : searchPagination.page.value
            : --searchPagination.page.value,
          size: searchPagination.limit.value || 25,
        })
      );
    } else {
      return JSON.parse(
        JSON.stringify({
          searchKey: search.value || undefined,
          search: search.value || undefined,
          page: next
            ? !current
              ? ++pagination.page.value
              : pagination.page.value
            : --pagination.page.value,
          size: pagination.limit.value || 25,
        })
      );
    }
  }

  function fetch(next = true, current = false, cache = false) {
    if (req.pending.value || (next && pagination.done.value)) return;

    // if(cache && paginationOptions.value.store && paginationOptions.value.store.getAll()?.length) return

    req.send(
      () => paginationOptions.value.cb(getPaginationData(next, current)),
      (res) => {
        if (paginationOptions.value.store && res.success) {
          console.log(res);
          // Fix: Store only the response array, not the entire res.data
          paginationOptions.value.store.set(res.data?.response || []);
        }

        pagination.totalPages.value = res.data?.totalPages || 1;
        if (
          res.success &&
          res.data?.response?.length < pagination.limit.value
        ) {
          pagination.done.value = true;
        }
      },
      true
    );
  }

  let controller;
  let timeout;
  function fetchSearch(next = true, current = false) {
    if (next && searchPagination.done.value) return;

    if (controller) controller.abort();
    if (timeout) clearTimeout(timeout);
    controller = new AbortController();

    timeout = setTimeout(() => {
      req.send(
        () =>
          paginationOptions.value.cb(getPaginationData(next, current), {
            signal: controller.signal,
          }),
        (res) => {
          searchPagination.totalPages.value = res.data?.totalPages || 1;
          if (
            res?.success &&
            res.data?.response?.length < searchPagination.limit.value
          ) {
            searchPagination.done.value = true;
          }
        },
        true
      );
    }, 20);
  }

  function next() {
    if (searching.value) {
      fetchSearch();
    } else {
      fetch(true, false, paginationOptions.value.cache);
    }
  }

  function previous() {
    if (searching.value && searchPagination.page.value == 1) return;
    if (!searching.value && pagination.page.value == 1) return;

    if (searching.value) {
      fetchSearch(false);
      searchPagination.done.value = false;
    } else {
      pagination.done.value = false;
      fetch(false, false, paginationOptions.value.cache);
    }
  }

  watch(search, () => {
    searchPagination.done.value = false;
    searchPagination.page.value = 0;
    if (search.value) {
      searching.value = true;
      fetchSearch(true, false);
    } else if (!search.value && paginationOptions.value.auto) {
      searching.value = false;
      pagination.done.value = false;
      fetch(true, true, paginationOptions.value.cache);
    }
  });

  const auto = computed(() => paginationOptions.value.auto);
  watch(auto, fetch, {
    immediate: paginationOptions.value.auto,
  });

  watch(perPage, () => {
    pagination.reset(perPage.value);
    searchPagination.reset(perPage.value);
    if (search.value) {
      searching.value = true;
      fetchSearch(true, true);
    } else {
      searching.value = false;
      fetch(true, true, paginationOptions.value.cache);
    }
  });

  provide("next", next);
  provide("previous", previous);
  provide("searchPage", searchPagination.page);
  provide("searchTotalPages", searchPagination.totalPages);
  provide("page", pagination.page);
  provide("totalPages", pagination.totalPages);
  provide("searching", searching);

  const page = computed(() => {
    return searching.value
      ? searchPagination.page.value
      : pagination.page.value;
  });

  function send() {
    pagination.reset()
    searchPagination.reset()
    fetch()
  }

  return {
    page,
    search,
    send,
    perPage,
    totalPages: req.response.value?.totalPages || 0,
    data:
      paginationOptions.value.store && !searching.value
        ? paginationOptions.value.store.getAll()
        : req.response || [],
    error: req.error,
    pending: req.pending,
    dirty: req.dirty,
    next,
    previous,
  };
}





