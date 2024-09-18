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
