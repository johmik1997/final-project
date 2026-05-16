import { effectScope, nextTick, watch } from "vue";
import { activeLocale, translateLiteralPreserveWhitespace } from "./index";

const TRANSLATABLE_ATTRIBUTES = ["placeholder", "title", "aria-label"];
const SKIPPED_TAG_NAMES = new Set([
  "CODE",
  "IFRAME",
  "NOSCRIPT",
  "PRE",
  "SCRIPT",
  "STYLE",
  "TEXTAREA",
]);

function toDatasetKey(attributeName) {
  return `i18nOriginal${attributeName
    .replace(/-([a-z])/g, (_, value) => value.toUpperCase())
    .replace(/^[a-z]/, (value) => value.toUpperCase())}`;
}

function shouldSkipNode(node) {
  const parentElement = node?.parentElement;
  if (!parentElement) return true;
  if (parentElement.closest("[data-i18n-skip='true']")) return true;
  return SKIPPED_TAG_NAMES.has(parentElement.tagName);
}

function translateTextNode(textNode) {
  if (!textNode || shouldSkipNode(textNode)) return;

  const originalValue =
    textNode.__i18nOriginalValue == null
      ? textNode.nodeValue
      : textNode.__i18nOriginalValue;

  if (textNode.__i18nOriginalValue == null) {
    textNode.__i18nOriginalValue = originalValue;
  }

  const translatedValue = translateLiteralPreserveWhitespace(originalValue);
  if (textNode.nodeValue !== translatedValue) {
    textNode.nodeValue = translatedValue;
  }
}

function translateAttributes(element) {
  if (!element || SKIPPED_TAG_NAMES.has(element.tagName)) return;
  if (element.closest("[data-i18n-skip='true']")) return;

  for (const attributeName of TRANSLATABLE_ATTRIBUTES) {
    if (!element.hasAttribute(attributeName)) continue;

    const datasetKey = toDatasetKey(attributeName);
    const currentValue = element.getAttribute(attributeName);
    const originalValue = element.dataset[datasetKey] || currentValue;

    if (!element.dataset[datasetKey]) {
      element.dataset[datasetKey] = originalValue || "";
    }

    const translatedValue = translateLiteralPreserveWhitespace(originalValue);
    if (currentValue !== translatedValue) {
      element.setAttribute(attributeName, translatedValue);
    }
  }
}

function translateSubtree(rootNode) {
  if (!rootNode) return;

  if (rootNode.nodeType === Node.TEXT_NODE) {
    translateTextNode(rootNode);
    return;
  }

  if (
    rootNode.nodeType !== Node.ELEMENT_NODE &&
    rootNode.nodeType !== Node.DOCUMENT_FRAGMENT_NODE
  ) {
    return;
  }

  const rootElement = rootNode.nodeType === Node.ELEMENT_NODE ? rootNode : null;
  if (rootElement) {
    translateAttributes(rootElement);
  }

  const attributeElements =
    rootNode.querySelectorAll instanceof Function
      ? rootNode.querySelectorAll("*")
      : [];
  attributeElements.forEach((element) => translateAttributes(element));

  const walker = document.createTreeWalker(rootNode, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) {
    textNodes.push(walker.currentNode);
  }
  textNodes.forEach((textNode) => translateTextNode(textNode));
}

function observeDomChanges() {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "characterData") {
        translateTextNode(mutation.target);
        continue;
      }

      if (mutation.type === "attributes") {
        translateAttributes(mutation.target);
        continue;
      }

      mutation.addedNodes.forEach((node) => translateSubtree(node));
    }
  });

  observer.observe(document.body, {
    subtree: true,
    childList: true,
    characterData: true,
    attributes: true,
    attributeFilter: TRANSLATABLE_ATTRIBUTES,
  });

  return observer;
}

export default {
  install(app) {
    if (typeof window === "undefined" || typeof document === "undefined") {
      return;
    }

    const scope = effectScope();

    scope.run(() => {
      watch(
        activeLocale,
        async () => {
          document.documentElement.lang = activeLocale.value;
          await nextTick();
          translateSubtree(document.body);
        },
        { immediate: true }
      );
    });

    const observer = observeDomChanges();

    app.config.globalProperties.$translateLiteral = translateLiteralPreserveWhitespace;
    app.provide("translateLiteral", translateLiteralPreserveWhitespace);

    window.addEventListener("beforeunload", () => {
      observer.disconnect();
      scope.stop();
    });
  },
};
