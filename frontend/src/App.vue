<template>
  <br><br><br><br>
  <div id="app">
    <ErrorMessage :message="errorMessage" />
    <SuccessMessage :message="successMessage" />
    <br>
    <DataTable ref="dataTable" />
    <br><br><br><br><br>
    <EnterData @data-updated="handleDataUpdated" />
    <br><br><br><br>
    <!--<MoneyGraph />
    <br><br><br><br>
    <ProductGraph />
    <br><br><br><br> -->
  </div>
  <br><br><br><br>
</template>

<script>
import axios from 'axios'
import DataTable from './components/DataTable.vue'
import EnterData from './components/EnterData.vue'
import ErrorMessage from './components/ErrorMessage.vue'
import SuccessMessage from './components/SuccessMessage.vue'
// import MoneyGraph from './components/MoneyGraph.vue'
// import ProductGraph from './components/ProductGraph.vue'

export default {
  name: 'App',
  components: {
    DataTable,
    EnterData,
    ErrorMessage,
    SuccessMessage // ,
    // MoneyGraph,
    // ProductGraph
  },
  data () {
    return {
      errorMessage: '',
      successMessage: ''
    }
  },
  methods: {
    handleDataUpdated () {
      this.$refs.dataTable.fetchData()
    },
    setError (message) {
      this.errorMessage = message
      setTimeout(() => {
        this.errorMessage = ''
      }, 10000)
    },
    setSuccess (message) {
      this.successMessage = message
      setTimeout(() => {
        this.successMessage = ''
      }, 10000)
    },
    setupGlobalErrorHandling () {
      // Intercept HTTP responses globally
      axios.interceptors.response.use(
        response => {
          const status = response.status
          if (status === 205 || status === 201 || status === 204) {
            let successMessage = ''
            if (status === 205) successMessage = 'Update completed successfully!'
            if (status === 201) successMessage = 'New entry created successfully!'
            if (status === 204) successMessage = 'Entry deleted successfully!'
            this.setSuccess(successMessage)
          }
          return response
        },
        error => {
          const status = error.response ? error.response.status : null
          const errorMessage = error.response && error.response.data && error.response.data.error
            ? error.response.data.error
            : 'An unexpected error occurred'

          if (status === 400 || status === 404 || status === 500) {
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
