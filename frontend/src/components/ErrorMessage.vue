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
  z-index: 9999;
  background: #f44336;
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>
