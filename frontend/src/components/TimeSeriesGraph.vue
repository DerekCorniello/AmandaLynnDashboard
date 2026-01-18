<template>
  <div class="graph-container">
    <div class="graph-header">
      <h3>Time Series Analysis</h3>
    </div>
    <div class="controls">
      <div class="control-group">
        <label>Years:</label>
        <div class="checkbox-group">
          <label v-for="year in availableYears" :key="year" class="checkbox-label">
            <input
              type="checkbox"
              :value="year"
              v-model="selectedYears"
              @change="fetchData"
            >
            {{ year }}
          </label>
        </div>
      </div>
      <div class="control-group">
        <label>Metrics:</label>
        <div class="checkbox-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              value="revenue"
              v-model="selectedMetrics"
              @change="fetchData"
            >
            Revenue
          </label>
          <label class="checkbox-label">
            <input
              type="checkbox"
              value="loss"
              v-model="selectedMetrics"
              @change="fetchData"
            >
            Loss
          </label>
          <label class="checkbox-label">
            <input
              type="checkbox"
              value="profit"
              v-model="selectedMetrics"
              @change="fetchData"
            >
            Profit
          </label>
          <label class="checkbox-label">
            <input
              type="checkbox"
              value="product_sales"
              v-model="selectedMetrics"
              @change="fetchData"
            >
            Product Sales
          </label>
        </div>
      </div>
      <div class="control-group" v-if="selectedMetrics.includes('product_sales')">
        <label>Products:</label>
        <select v-model="selectedProductsMode" @change="fetchData">
          <option value="all">All Products</option>
          <option value="selected">Selected Products</option>
        </select>
        <div v-if="selectedProductsMode === 'selected'" class="checkbox-group">
          <label v-for="product in availableProducts" :key="product.name" class="checkbox-label">
            <input
              type="checkbox"
              :value="product.name"
              v-model="selectedProducts"
              @change="fetchData"
            >
            {{ toTitleCase(product.name) }}
          </label>
        </div>
      </div>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="hasData" class="chart-wrapper">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="no-data">No data available for selected options</div>
  </div>
</template>

<script>
import axios from 'axios'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

export default {
  name: 'TimeSeriesGraph',
  components: {
    Line
  },
  data () {
    return {
      loading: true,
      error: null,
      chartData: null,
      selectedYears: [new Date().getFullYear()],
      selectedMetrics: ['revenue', 'profit'],
      selectedProductsMode: 'all',
      selectedProducts: [],
      availableProducts: []
    }
  },
  computed: {
    hasData () {
      return this.chartData && this.chartData.labels && this.chartData.labels.length > 0
    },
    availableYears () {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let i = currentYear - 5; i <= currentYear + 1; i++) {
        years.push(i)
      }
      return years
    },
    chartOptions () {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          datalabels: {
            display: false
          },
          title: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#333',
            bodyColor: '#333',
            borderColor: '#ddd',
            borderWidth: 1,
            mode: 'index',
            intersect: false
          },
          legend: {
            position: 'top',
            labels: {
              color: '#ffffff',
              font: {
                size: 12,
                weight: 'normal'
              },
              padding: 15,
              usePointStyle: true,
              pointStyle: 'circle'
            }
          }
        },
        scales: {
          x: {
            stacked: false,
            ticks: {
              color: '#fff',
              maxRotation: 45,
              minRotation: 0
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          y: {
            stacked: false,
            beginAtZero: true,
            ticks: {
              color: '#fff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      }
    }
  },
  async mounted () {
    await this.fetchProducts()
    await this.fetchData()
  },
  methods: {
    toTitleCase (str) {
      if (!str) return ''
      if (typeof str !== 'string') return str
      // Replace underscores with spaces first
      str = str.replace(/_/g, ' ')
      // Then apply title case
      return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
    },
    async fetchProducts () {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/products/?show_retired=false')
        this.availableProducts = response.data
      } catch (err) {
        console.error('Error fetching products:', err)
      }
    },
    async fetchData () {
      this.loading = true
      this.error = null

      try {
        const params = {
          graph: 'timeseries',
          timescale: 'all',
          years: this.selectedYears.join(','),
          metrics: this.selectedMetrics.join(',')
        }

        if (this.selectedMetrics.includes('product_sales')) {
          if (this.selectedProductsMode === 'all') {
            params.products = 'all'
          } else {
            if (this.selectedProducts.length === 0) {
              this.chartData = null
              this.loading = false
              return
            }
            params.products = this.selectedProducts.join(',')
          }
        } else {
          params.products = ''
        }

        const response = await axios.post('http://127.0.0.1:8000/api/graphdata/', params)

        this.chartData = {
          labels: response.data.labels,
          datasets: response.data.datasets.map((dataset) => ({
            ...dataset,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 0,
            tension: 0.1
          }))
        }
      } catch (err) {
        this.error = 'Failed to load time series data'
        console.error('Error fetching time series data:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.graph-container {
  width: 100%;
  max-width: 1200px;
  padding: 30px 20px;
  margin-top: 40px;
}

.graph-header {
  text-align: center;
  margin-bottom: 25px;
}

.graph-container h3 {
  margin: 0;
  color: #fff;
  font-size: 24px;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  margin-bottom: 25px;
}

.control-group {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  min-width: 150px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-group label {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.control-group select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.control-group select option {
  background: #2c2c2c;
  color: #fff;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.chart-wrapper {
  position: relative;
  height: 500px;
  width: 100%;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 40px;
  color: #fff;
  font-size: 16px;
}

.error {
  color: #e53935;
}
</style>
