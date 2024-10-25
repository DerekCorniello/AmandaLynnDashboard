<template>
  <div v-if="message" class="success-message">
    {{ message }}
  </div>
</template>

<script>
export default {
  props: ['message']
}
</script>

<style scoped>
.success-message {
  position: fixed;
  top: 1%;
  left: 50%;
  transform: translateX(-50%);
}
</style>
