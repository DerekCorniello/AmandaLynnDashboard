<template>
  <br> <br> <br> <br>
  <div id="app">
    <ErrorMessage :message="errorMessage" />
    <br>
    <DataTable />
    <br> <br> <br> <br> <br>
    <EnterData @data-updated="handleDataUpdated"/>
  <br> <br> <br> <br>
  </div>
  <br> <br> <br> <br>
</template>

<script>
import axios from 'axios'
import DataTable from './components/DataTable.vue'
import EnterData from './components/EnterData.vue'
import ErrorMessage from './components/ErrorMessage.vue'

export default {
  name: 'App',
  components: {
    DataTable,
    EnterData,
    ErrorMessage
  },
  data () {
    return {
      errorMessage: ''
    }
  },
  methods: {
    handleDataUpdated (table) {
      this.$refs.dataTable.fetchData()
    },
    setError (message) {
      this.errorMessage = message
      setTimeout(() => {
        this.errorMessage = ''
      }, 10000) // Clear the message after 10 seconds
    },
    setupGlobalErrorHandling () {
      // Intercept HTTP errors globally
      axios.interceptors.response.use(
        response => response,
        error => {
          const status = error.response ? error.response.status : null
          const errorMessage = error.response && error.response.data && error.response.data.error
            ? error.response.data.error
            : 'An unexpected error occurred'

          if (status === 400 || status === 404) {
            this.setError(`Error ${status}: ${errorMessage}`)
          }

          return Promise.reject(error)
        }
      )
    }
  },
  created () {
    this.setupGlobalErrorHandling()
  }
}
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80%;
  text-align: center;
}
</style>
