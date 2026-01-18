<template>
  <div class="export-container">
    <div class="export-header">
      <h3>Export Data</h3>
    </div>
    <div class="export-controls">
      <div class="control-group">
        <label>Data Type:</label>
        <select v-model="selectedDataType">
          <option value="all">All Data</option>
          <option value="products">Products Only</option>
          <option value="expenses">Expenses Only</option>
          <option value="transactions">Transactions Only</option>
        </select>
      </div>
      <div class="control-group">
        <label>Format:</label>
        <div class="format-segmented">
          <label class="format-segment" :class="{ active: selectedFormat === 'txt' }">
            <input type="radio" v-model="selectedFormat" value="txt">
            <span>TXT</span>
          </label>
          <label class="format-segment" :class="{ active: selectedFormat === 'pdf' }">
            <input type="radio" v-model="selectedFormat" value="pdf">
            <span>PDF</span>
          </label>
          <label class="format-segment" :class="{ active: selectedFormat === 'docx' }">
            <input type="radio" v-model="selectedFormat" value="docx">
            <span>DOCX</span>
          </label>
        </div>
      </div>
      <button
        @click="exportData"
        :disabled="isExporting"
        class="export-button"
      >
        {{ isExporting ? 'Exporting...' : 'Download Export' }}
      </button>
    </div>
    <div v-if="exportStatus" class="export-status" :class="exportStatus.type">
      {{ exportStatus.message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ExportPanel',
  data () {
    return {
      selectedDataType: 'all',
      selectedFormat: 'txt',
      isExporting: false,
      exportStatus: null
    }
  },
  methods: {
    async exportData () {
      if (this.isExporting) return

      this.isExporting = true
      this.exportStatus = null

      try {
        const url = 'http://127.0.0.1:8000/api/export/'
        const params = {
          type: this.selectedDataType,
          format: this.selectedFormat
        }

        const response = await axios.get(url, {
          params: params,
          responseType: 'blob'
        })

        const contentType = response.headers['content-type']
        const contentDisposition = response.headers['content-disposition']
        let filename = `export_${Date.now()}`
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }

        const blob = new Blob([response.data], { type: contentType })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(link.href)

        this.exportStatus = {
          type: 'success',
          message: `Export downloaded successfully as ${filename}`
        }
        setTimeout(() => {
          this.exportStatus = null
        }, 5000)
      } catch (error) {
        console.error('Export failed:', error)
        this.exportStatus = {
          type: 'error',
          message: 'Export failed. Please try again.'
        }
        setTimeout(() => {
          this.exportStatus = null
        }, 5000)
      } finally {
        this.isExporting = false
      }
    }
  }
}
</script>

<style scoped>
.export-container {
  width: 100%;
  max-width: 600px;
  padding: 25px 20px;
  margin: 30px auto;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.export-header {
  text-align: center;
  margin-bottom: 20px;
}

.export-header h3 {
  margin: 0;
  color: #fff;
  font-size: 22px;
}

.export-controls {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  margin-bottom: 0px;
}

.control-group label {
  color: #ccc;
  font-size: 14px;
  font-weight: 500;
}

.control-group select {
  padding: 10px 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.control-group select option {
  background: #2c2c2c;
  color: #fff;
}

.format-segmented {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 4px;
  gap: 0;
}

.format-segment {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  color: #aaa;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  position: relative;
  font-weight: 500;
  font-size: 14px;
  margin-bottom: !important 0px;
}

.format-segment:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.format-segment.active {
  background: #7c4dff;
  color: #fff;
  font-weight: 600;
}

.format-segment input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.export-button {
  background: #7c4dff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
  margin-top: 10px;
}

.export-button:hover:not(:disabled) {
  background: #6a1b9a;
  transform: translateY(-1px);
}

.export-button:disabled {
  background: #555;
  cursor: not-allowed;
  transform: none;
}

.export-status {
  margin-top: 15px;
  padding: 12px;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
}

.export-status.success {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.export-status.error {
  background: rgba(244, 67, 54, 0.2);
  color: #e57373;
  border: 1px solid rgba(244, 67, 54, 0.3);
}
</style>
