/** Normalize barcode / ISBN text from scanner hardware. */
export function normalizeBarcodeValue(raw) {
  const text = String(raw || '').trim();
  if (!text) return '';

  const digitsOnly = text.replace(/\D/g, '');
  if (digitsOnly.length === 10 || digitsOnly.length === 13) {
    return digitsOnly;
  }
  return text;
}
