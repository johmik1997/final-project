/**
 * Set a form builder field value by name (works with Input/Select custom-input elements).
 */
export function setFormFieldValue(formId, fieldName, value) {
  const form = document.getElementById(formId);
  if (!form) return false;

  const input = form.querySelector(`[name="${fieldName}"]`);
  if (!input) return false;

  const nextValue = value ?? '';

  if (input.type === 'file') {
    return false;
  }

  input.value = nextValue;
  input.dataset.val = JSON.stringify({ value: nextValue });
  input.dataset.valid = 'true';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  return true;
}
