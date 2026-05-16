<script setup>
import { defineProps, ref, onMounted, onUnmounted, nextTick, watchEffect } from 'vue';

const props = defineProps({
  position: {
    type: String, // "left-bottom" | "right-bottom" | "left-top" | "right-top"
    default: "left-bottom",
  },
  offset: {
    type: Number,
    default: 8,
  },
  disabled: {
    type: Boolean,
    default: false,
  }
});

const dropdownWrapper = ref();
const openDropdown = ref(false);
const isAnimating = ref(false);

function setRef(el) {
  dropdownWrapper.value = el;
}

// Close dropdown when clicking outside
function handleClickOutside(event) {
  if (dropdownWrapper.value && !dropdownWrapper.value.contains(event.target)) {
    closeDropdown();
  }
}

// Close on escape key
function handleKeyDown(event) {
  if (event.key === 'Escape') {
    closeDropdown();
  }
}

async function openDropdownMenu() {
  if (props.disabled || isAnimating.value) return;
  
  isAnimating.value = true;
  openDropdown.value = true;
  
  await nextTick();
  
  if (dropdownWrapper.value) {
    dropdownWrapper.value.classList.add("__dropdown-wrapper", props.position);
    dropdownWrapper.value.style.setProperty('--offset', `${props.offset}px`);
    
    // Trigger enter animation
    requestAnimationFrame(() => {
      dropdownWrapper.value?.classList.add('__dropdown-enter');
      setTimeout(() => {
        isAnimating.value = false;
      }, 200);
    });
  }
}

async function closeDropdown() {
  if (isAnimating.value) return;
  
  isAnimating.value = true;
  
  if (dropdownWrapper.value) {
    dropdownWrapper.value.classList.add('__dropdown-leave');
    
    setTimeout(() => {
      openDropdown.value = false;
      if (dropdownWrapper.value) {
        dropdownWrapper.value.classList.remove('__dropdown-enter', '__dropdown-leave');
      }
      isAnimating.value = false;
    }, 150);
  } else {
    openDropdown.value = false;
    isAnimating.value = false;
  }
}

async function toggle() {
  if (props.disabled || isAnimating.value) return;
  
  if (openDropdown.value) {
    closeDropdown();
  } else {
    openDropdownMenu();
  }
}

// Position dropdown properly
function positionDropdown() {
  if (!dropdownWrapper.value) return;
  
  const rect = dropdownWrapper.value.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  const viewportWidth = window.innerWidth;
  
  // Auto-adjust position if dropdown would go off-screen
  let finalPosition = props.position;
  
  if (props.position.includes('bottom') && rect.bottom > viewportHeight - 20) {
    finalPosition = props.position.replace('bottom', 'top');
  }
  
  if (props.position.includes('right') && rect.right > viewportWidth - 20) {
    finalPosition = finalPosition.replace('right', 'left');
  }
  
  dropdownWrapper.value.className = dropdownWrapper.value.className.replace(
    /\b(left|right)-(top|bottom)\b/g, 
    finalPosition
  );
}

// Watch for dropdown state changes
watchEffect(() => {
  if (openDropdown.value) {
    document.addEventListener("click", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    nextTick(() => {
      positionDropdown();
    });
  } else {
    document.removeEventListener("click", handleClickOutside);
    document.removeEventListener("keydown", handleKeyDown);
  }
});

onMounted(() => {
  if (openDropdown.value) {
    positionDropdown();
  }
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
  document.removeEventListener("keydown", handleKeyDown);
});
</script>
<template>
  <div 
    @click.prevent.stop="() => {}" 
    class="relative inline-block"
    :class="{ 'pointer-events-none': disabled }"
  >
    <slot 
      :toggle="toggle" 
      :setRef="setRef" 
      :open="openDropdown"
      :disabled="disabled"
      :toggleDropdown="toggle"
    />
  </div>
</template>

<style>
.__dropdown-wrapper {
  position: absolute;
  z-index: 1000;
  min-width: 160px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(8px);
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  overflow: hidden;
}

.__dropdown-wrapper.__dropdown-enter {
  opacity: 1;
  transform: scale(1) translateY(0);
  pointer-events: auto;
}

.__dropdown-wrapper.__dropdown-leave {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
  pointer-events: none;
}

/* Position classes */
.left-bottom {
  top: calc(100% + var(--offset, 8px));
  left: 0;
  transform-origin: top left;
}

.right-bottom {
  top: calc(100% + var(--offset, 8px));
  right: 0;
  transform-origin: top right;
}

.left-top {
  bottom: calc(100% + var(--offset, 8px));
  left: 0;
  transform-origin: bottom left;
}

.right-top {
  bottom: calc(100% + var(--offset, 8px));
  right: 0;
  transform-origin: bottom right;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .__dropdown-wrapper {
    background: rgba(31, 41, 55, 0.95);
    border-color: rgba(75, 85, 99, 0.3);
    color: white;
  }
}

/* Dropdown content styling */
.__dropdown-wrapper .dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  font-size: 14px;
  color: #374151;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  border-radius: 4px;
  margin: 2px;
}

.__dropdown-wrapper .dropdown-item:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.__dropdown-wrapper .dropdown-item:focus {
  outline: none;
  background-color: #e5e7eb;
}

.__dropdown-wrapper .dropdown-item.danger {
  color: #dc2626;
}

.__dropdown-wrapper .dropdown-item.danger:hover {
  background-color: #fef2f2;
  color: #b91c1c;
}

.__dropdown-wrapper .dropdown-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.__dropdown-wrapper .dropdown-divider {
  height: 1px;
  background-color: #e5e7eb;
  margin: 4px 0;
}

/* Animation improvements for mobile */
@media (max-width: 768px) {
  .__dropdown-wrapper {
    min-width: 200px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  }
}

/* Accessibility improvements */
.__dropdown-wrapper:focus-within {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
