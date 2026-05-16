<script setup >
import ModalParent from '@/components/new_form_builder/ModalParent.vue';
import SecurityForm from './SecurityForm.vue';
import NewFormParent from '@/components/NewFormParent.vue';

</script>

<template>
  <ModalParent>
    <NewFormParent 
      class="" 
      size="xs" 
      title="Change Your Password" 
      subtitle="Keep your account secure by setting a new password."
    >
      <SecurityForm />
    </NewFormParent>
  </ModalParent>
</template>