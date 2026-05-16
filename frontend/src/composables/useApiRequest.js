import { provide, ref } from "vue";

export function useApiRequest(provideValues = true) {
  const response = ref();
  const pending = ref(false);
  const error = ref("");
  const dirty = ref(false);

  if (provideValues) {
    provide("pending", pending);
    provide("error", error);
  }

  async function send(
    request = (f) => f,
    cb = (f) => f,
    remove = false
  ) {
    if (typeof request != "function") {
      console.error("can not be called. not a function");
      return null;
    }

    pending.value = true;
    error.value = "";

    if (remove) {
      response.value = null;
    }
    try {
      dirty.value = true;
      const res = await request();
      response.value = res?.data ?? res;
      error.value = res?.error || "";

      if (typeof cb == "function") {
        cb(res);
      }

      return res;
    } catch (err) {
      console.error(err);
      error.value = err?.message || "Request failed";
      return {
        success: false,
        data: null,
        status: err?.status || 500,
        error: error.value,
      };
    } finally {
      pending.value = false;
    }
  }

  return {
    response,
    send,
    pending,
    error,
    dirty,
  };
}
