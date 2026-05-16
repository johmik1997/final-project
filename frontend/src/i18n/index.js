import { computed, ref, unref } from "vue";
import {
  LITERAL_TRANSLATIONS,
  PATTERN_TRANSLATIONS,
  SUPPORTED_LOCALES,
} from "./translations";

const STORAGE_KEY = "preferred-language";
const FALLBACK_LOCALE = "en";

function getStoredLocale() {
  if (typeof window === "undefined") {
    return FALLBACK_LOCALE;
  }

  const storedValue = window.localStorage.getItem(STORAGE_KEY);
  return SUPPORTED_LOCALES.some((item) => item.code === storedValue)
    ? storedValue
    : FALLBACK_LOCALE;
}

export const activeLocale = ref(getStoredLocale());

function normalizeLiteralValue(value) {
  return String(value ?? "")
    .replace(/\u00a0/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function translateWithPatterns(value) {
  for (const entry of PATTERN_TRANSLATIONS) {
    if (entry.pattern.test(value)) {
      return value.replace(entry.pattern, entry.replacement);
    }
  }

  return value;
}

export function getLocaleCode(locale = activeLocale.value) {
  return locale === "am" ? "am-ET" : "en-US";
}

export function translateLiteral(value, locale = activeLocale.value) {
  const normalizedLocale = unref(locale) || FALLBACK_LOCALE;
  const literalValue = normalizeLiteralValue(value);

  if (!literalValue || normalizedLocale === "en") {
    return literalValue;
  }

  if (LITERAL_TRANSLATIONS[literalValue]) {
    return LITERAL_TRANSLATIONS[literalValue];
  }

  const punctuationMatch = literalValue.match(/^(.+?)([.!?:])$/);
  if (punctuationMatch) {
    const [, baseValue, punctuation] = punctuationMatch;
    if (LITERAL_TRANSLATIONS[baseValue]) {
      return `${LITERAL_TRANSLATIONS[baseValue]}${punctuation}`;
    }
  }

  return translateWithPatterns(literalValue);
}

export function translateLiteralPreserveWhitespace(value, locale = activeLocale.value) {
  const rawValue = String(value ?? "");
  if (!rawValue.trim()) {
    return rawValue;
  }

  const leadingWhitespace = rawValue.match(/^\s*/)?.[0] || "";
  const trailingWhitespace = rawValue.match(/\s*$/)?.[0] || "";
  const translatedValue = translateLiteral(rawValue, locale);

  return `${leadingWhitespace}${translatedValue}${trailingWhitespace}`;
}

export function setLocale(nextLocale) {
  const safeLocale = SUPPORTED_LOCALES.some((item) => item.code === nextLocale)
    ? nextLocale
    : FALLBACK_LOCALE;

  activeLocale.value = safeLocale;

  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, safeLocale);
  }

  if (typeof document !== "undefined") {
    document.documentElement.lang = safeLocale;
  }
}

if (typeof document !== "undefined") {
  document.documentElement.lang = activeLocale.value;
}

export function useI18n() {
  return {
    locale: activeLocale,
    locales: SUPPORTED_LOCALES,
    isAmharic: computed(() => activeLocale.value === "am"),
    setLocale,
    t: (value) => translateLiteral(value),
  };
}
