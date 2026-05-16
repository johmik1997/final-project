const ENTITY_MUTATION_EVENT = "app:entity-mutation";

export function emitEntityMutation(entity, payload = {}) {
  if (typeof window === "undefined" || !entity) return;

  window.dispatchEvent(
    new CustomEvent(ENTITY_MUTATION_EVENT, {
      detail: {
        entity,
        ...payload,
      },
    })
  );
}

export function subscribeEntityMutation(entity, callback) {
  if (typeof window === "undefined" || typeof callback !== "function") {
    return () => {};
  }

  const handler = (event) => {
    const detail = event?.detail || {};
    if (entity !== "*" && detail.entity !== entity) return;
    callback(detail);
  };

  window.addEventListener(ENTITY_MUTATION_EVENT, handler);
  return () => window.removeEventListener(ENTITY_MUTATION_EVENT, handler);
}
