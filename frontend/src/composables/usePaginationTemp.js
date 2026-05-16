import { computed, provide, ref, watch } from "vue";
import { useTablePagination } from "./useTablePagination";
import { useApiRequest } from "./useApiRequest";

export function usePaginations(options = {}) {
  const paginationOptions = ref({
    cb: (f) => f,
    store: null,
    auto: true,
    perPage: 5,
    cache: false,
    ...(options || {}),
  });

  const search = ref("");
  const perPage = ref(paginationOptions.value.perPage);

  const req = useApiRequest(); // This has req.pending

  const searching = ref(false);
  const searchPagination = useTablePagination(perPage.value);
  const pagination = useTablePagination(perPage.value);
  const totalElements = ref(0);
  pagination.page.value = 1;
  searchPagination.page.value = 1;

  function getRowsFromPayload(payload) {
    if (!payload) return [];
    const rows =
      payload.response ??
      payload.content ??
      payload.result ??
      payload.results ??
      payload.libraries ??
      payload.users ??
      payload;
    return Array.isArray(rows) ? rows : [];
  }

  function normalizeQuery(query) {
    return Object.fromEntries(
      Object.entries(query || {}).filter(([, value]) => value !== undefined && value !== null && value !== "")
    );
  }

  function updatePaginationMeta(payload = {}) {
    const rows = getRowsFromPayload(payload);
    const totalPages = payload.totalPages ?? payload.number_of_pages ?? 1;
    const size = payload.size ?? perPage.value;
    const count = payload.totalElements ?? payload.count ?? rows.length;
    const pageOneBased = payload.page ?? ((payload.number ?? 0) + 1);

    pagination.totalPages.value = Number(totalPages) || 1;
    perPage.value = Number(size) || perPage.value;
    pagination.limit.value = perPage.value;
    searchPagination.limit.value = perPage.value;
    totalElements.value = Number(count) || 0;
    pagination.page.value = Number(pageOneBased) || 1;
  }

  function getPaginationData(next = true, current = false) {
    const activePagination = searching.value ? searchPagination : pagination;
    let targetPage = Number(activePagination.page.value) || 1;
    if (!current) {
      targetPage = next ? targetPage + 1 : targetPage - 1;
    }
    targetPage = Math.max(targetPage, 1);
    activePagination.page.value = targetPage;

    return normalizeQuery(
      JSON.parse(
        JSON.stringify({
          searchKey: search.value || undefined,
          search: search.value || undefined,
          page: targetPage,
          size: Number(perPage.value) || Number(activePagination.limit.value) || 5,
        })
      )
    );
  }

  async function fetch(next = true, current = false, cache = false) {
    if (req.pending.value || (next && pagination.done.value)) return;

    return req.send(
      () => paginationOptions.value.cb(getPaginationData(next, current)),
      (res) => {
        if (paginationOptions.value.store && res.success) {
          paginationOptions.value.store.set(getRowsFromPayload(res.data));
        }

        updatePaginationMeta(res.data || {});
        if (
          res.success &&
          getRowsFromPayload(res.data).length < pagination.limit.value
        ) {
          pagination.done.value = true;
        }
      },
      true
    );
  }

  let controller;
  let timeout;
  async function fetchSearch(next = true, current = false) {
    if (next && searchPagination.done.value) return;

    if (controller) controller.abort();
    if (timeout) clearTimeout(timeout);
    controller = new AbortController();

    return new Promise((resolve) => {
      timeout = setTimeout(() => {
        req.send(
          () =>
            paginationOptions.value.cb(getPaginationData(next, current), {
              signal: controller.signal,
            }),
          (res) => {
            if (paginationOptions.value.store && res.success) {
              paginationOptions.value.store.set(getRowsFromPayload(res.data));
            }

            searchPagination.totalPages.value = res.data?.totalPages || res.data?.number_of_pages || 1;
            totalElements.value = res.data?.totalElements ?? res.data?.count ?? totalElements.value;
            if (
              res?.success &&
              getRowsFromPayload(res.data).length < searchPagination.limit.value
            ) {
              searchPagination.done.value = true;
            }

            resolve(res);
          },
          true
        );
      }, 20);
    });
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

  function goToPage(page) {
    const pageNum = Number(page);
    if (!pageNum || pageNum < 1) return;

    if (searching.value) {
      searchPagination.page.value = pageNum;
      searchPagination.done.value = false;
      fetchSearch(true, true);
      return;
    }

    pagination.page.value = pageNum;
    pagination.done.value = false;
    fetch(true, true, paginationOptions.value.cache);
  }

  function setPerPage(size) {
    const nextSize = Number(size);
    if (!nextSize || nextSize < 1) return;
    perPage.value = nextSize;
    pagination.limit.value = nextSize;
    searchPagination.limit.value = nextSize;
    pagination.page.value = 1;
    searchPagination.page.value = 1;
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
  watch(
    auto,
    (enabled) => {
      if (!enabled) return;
      pagination.page.value = Math.max(Number(pagination.page.value) || 1, 1);
      searchPagination.page.value = Math.max(Number(searchPagination.page.value) || 1, 1);
      fetch(true, true, paginationOptions.value.cache);
    },
    {
      immediate: paginationOptions.value.auto,
    }
  );

  watch(perPage, () => {
    pagination.limit.value = perPage.value;
    searchPagination.limit.value = perPage.value;
    pagination.page.value = 1;
    searchPagination.page.value = 1;
    pagination.done.value = false;
    searchPagination.done.value = false;
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
 async function send() {
    try {
      req.pending.value = true;
      
      const response = await paginationOptions.value.cb(
        {
          page: Math.max(pagination.page.value || 0, 1),
          size: perPage.value, // Use 'size' instead of 'limit' to match your API
          ...(search.value ? { search: search.value } : {}),
          ...paginationOptions.value.params
        },
        paginationOptions.value.config
      );
      
      if (response && response.data) {
        const rows = getRowsFromPayload(response.data);
        
        updatePaginationMeta(response.data);
        
        if (paginationOptions.value.store && typeof paginationOptions.value.store.set === 'function') {
          paginationOptions.value.store.set(rows);
        }
      }
      
      return response;
    } catch (error) {
      console.error('Pagination error:', error);
      req.error.value = error; // Set error on req
      return { success: false, error: error.message };
    } finally {
      req.pending.value = false; // Use req.pending instead of pending
    }
  }

  function refresh() {
    pagination.done.value = false;
    searchPagination.done.value = false;

    if (search.value) {
      return fetchSearch(true, true);
    }

    return fetch(true, true, paginationOptions.value.cache);
  }

  return {
    page: computed(() => searching.value ? searchPagination.page.value : pagination.page.value),
    search,
    send,
    refresh,
    perPage,
    meta: computed(() => ({
      number: Math.max((pagination.page.value || 1) - 1, 0),
      totalPages: pagination.totalPages.value || 1,
      totalElements: totalElements.value || 0,
      size: perPage.value || 5,
      page: pagination.page.value || 1,
    })),
    totalPages: computed(() => searching.value ? searchPagination.totalPages.value : pagination.totalPages.value),
    data: computed(() => {
      if (paginationOptions.value.store && !searching.value) {
        return paginationOptions.value.store.getAll();
      }
      return getRowsFromPayload(req.response.value?.data || req.response.value);
    }),
    error: req.error,
    pending: req.pending, // Return req.pending
    dirty: req.dirty,
    next,
    previous,
    goToPage,
    setPerPage,
  };
}
