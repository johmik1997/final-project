import { ref, provide, nextTick } from "vue";

export function useForm(id, inner = true, childrenName) {
  if(!inner) return {}

  if(!id) {
    throw new Error("[id] is required")
  }

  const formEl = ref()
  const validateAll = ref(false);
  const valid = ref(false);
  const reset = ref(false);

  provide("validateAll", validateAll);
  provide("reset", reset);
  provide("id", id);

  function resetValue() {
    reset.value = true
    nextTick(() => {
      reset.value = false
      valid.value = false
    })
  }

  function submit(fun = f => f) {
    validateAll.value = true
    nextTick(() => {
      validateAll.value = false
      
      const selector = childrenName ? `.${childrenName}` : ".custom-input";
      const formFromRef = formEl.value;
      const formFromId = !formFromRef && id ? document.querySelector(`#${id}`) : null;
      const targetForm = formFromRef || formFromId;

      if (!targetForm) {
        throw new Error(`[useForm] no form found for id: ${id}`);
      }

      const inputs = targetForm.querySelectorAll(selector);
      if (!inputs) return false;

      const allValid = [...inputs].every(el => el.dataset["valid"] == "true")

      if(!allValid) return
      valid.value = true
      let values = [...inputs].reduce((state, el) => {
        const name = el.getAttribute("name");
        if (!name) return state;

        if(el.type == "file") {
          state[name] = el.val
        } else {
          try {
            state[name] = JSON.parse(el.dataset["val"])?.value;
          } catch {
            state[name] = el.value ?? "";
          }
        }
        return state
      }, {})

      fun({values, reset: resetValue})
    })
  }

  return {submit, id, formEl, valid, reset: resetValue}
}
