<template>
  <div v-if="message" class="error-message">
    {{ message }}
  </div>
</template>

<script>
export default {
  props: ['message']
}
</script>

<style scoped>
.error-message {
  position: fixed;
  top: 1%;
  left: 50%;
  transform: translateX(-50%);
}
</style>
