<template>
  <br><br><br><br>
  <div id="app">
    <!-- Footer with save functionality -->
    <div class="app-footer">
      <div class="save-controls">
        <button
          @click="manualSave"
          :disabled="isSaving"
          class="save-button"
        >
          {{ isSaving ? 'Saving...' : 'Save Data' }}
        </button>
        <span class="save-status" :class="saveStatusClass">
          {{ saveStatusText }}
        </span>
        <span class="autosave-indicator" v-if="autosaveEnabled">
          Autosave: {{ formatCountdown(autosaveCountdown) }}
        </span>
      </div>
    </div>

    <ErrorMessage :message="errorMessage" />
    <SuccessMessage :message="successMessage" />
    <EnterData @data-updated="handleDataUpdated" />
    <br>
    <br><br><br><br><br>
    <DataTable ref="dataTable" />
    <br><br><br><br>
     <ProductComparisonGraph />
     <br><br><br><br>
     <TimeSeriesGraph />
     <br><br><br><br>
  </div>
  <br><br><br><br>
</template>

<script>
import axios from 'axios'
import DataTable from './components/DataTable.vue'
import EnterData from './components/EnterData.vue'
import ErrorMessage from './components/ErrorMessage.vue'
import SuccessMessage from './components/SuccessMessage.vue'
import ProductComparisonGraph from './components/ProductComparisonGraph.vue'
import TimeSeriesGraph from './components/TimeSeriesGraph.vue'

export default {
  name: 'App',
  components: {
    DataTable,
    EnterData,
    ErrorMessage,
    SuccessMessage,
    ProductComparisonGraph,
    TimeSeriesGraph
  },
  data () {
    return {
      errorMessage: '',
      successMessage: '',
      isSaving: false,
      lastSaveTime: null,
      autosaveEnabled: true,
      autosaveInterval: 5 * 60 * 1000, // 5 minutes
      autosaveCountdown: 300, // 5 minutes in seconds
      countdownTimer: null
    }
  },
  computed: {
    saveStatusText () {
      if (this.isSaving) return 'Saving...'
      if (this.lastSaveTime) {
        return `Last saved: ${this.formatTime(this.lastSaveTime)}`
      }
      return 'Not saved yet'
    },
    saveStatusClass () {
      if (this.isSaving) return 'saving'
      if (this.lastSaveTime) return 'saved'
      return ''
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
    async manualSave () {
      if (this.isSaving) return

      this.isSaving = true
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/save/')
        if (response.data.status === 'saved') {
          this.lastSaveTime = new Date(response.data.timestamp)
          this.resetAutosaveTimer()
          this.setSuccess('Data saved successfully!')
        }
      } catch (error) {
        console.error('Save failed:', error)
        this.setError('Failed to save data')
      } finally {
        this.isSaving = false
      }
    },
    startAutosaveTimer () {
      if (!this.autosaveEnabled) return

      this.countdownTimer = setInterval(() => {
        this.autosaveCountdown--
        if (this.autosaveCountdown <= 0) {
          this.performAutosave()
        }
      }, 1000)
    },
    resetAutosaveTimer () {
      this.autosaveCountdown = 300 // Reset to 5 minutes
    },
    stopAutosaveTimer () {
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
    },
    async performAutosave () {
      if (this.isSaving) return

      try {
        const response = await axios.post('http://127.0.0.1:8000/api/save/')
        if (response.data.status === 'saved') {
          this.lastSaveTime = new Date(response.data.timestamp)
          this.resetAutosaveTimer()
          console.log('Autosave completed at', this.lastSaveTime.toLocaleTimeString())
        }
      } catch (error) {
        console.error('Autosave failed:', error)
        // Reset timer even on failure to avoid spam
        this.resetAutosaveTimer()
      }
    },
    formatTime (date) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    formatCountdown (seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
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
  },
  mounted () {
    this.startAutosaveTimer()
  },
  beforeUnmount () {
    this.stopAutosaveTimer()
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

.app-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #2c2c2c;
  border-top: 2px solid rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  z-index: 1000;
}

.save-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  justify-content: center;
}

.save-button {
  background: #7c4dff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.save-button:hover:not(:disabled) {
  background: #6a1b9a;
  transform: translateY(-1px);
}

.save-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.save-status {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.save-status.saved {
  color: #4CAF50;
}

.save-status.error {
  color: #ff6b6b;
}

.save-status.saving {
  color: #ffd93d;
}

.autosave-indicator {
  font-size: 12px;
  color: #ccc;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
}
</style>
