<template>
  <div>
    <h2>Products Sold Over Time</h2>

     <label>Select Products:</label>
     <select v-model="selectedProducts" @change="updateChart" multiple>
       <option v-for="product in products" :key="product.id" :value="product.id">{{ toTitleCase(product.name) }}</option>
     </select>

    <label>Time Scale:</label>
    <select v-model="selectedTimeScale" @change="updateChart">
      <option value="week">Last Week</option>
      <option value="month">Last Month</option>
      <option value="3months">Last 3 Months</option>
      <option value="6months">Last 6 Months</option>
      <option value="year">Last Year</option>
      <option value="all">All Time</option>
    </select>

    <line-chart :chart-data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js'
import titleCaseMixin from '../mixins/titleCaseMixin'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

export default {
  mixins: [titleCaseMixin],
  components: {
    LineChart: Line
  },
  data () {
    return {
      products: [], // Available products
      selectedProducts: [], // Selected product IDs
      selectedTimeScale: 'month',
      chartData: {
        labels: [], // Dates for the x-axis
        datasets: [] // Each selected product will get its own dataset
      },
      chartOptions: {
        responsive: true,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day'
            }
          }
        }
      }
    }
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
    updateChart () {
      // Fetch and update the chart data based on selected products and time scale
    }
  },
  mounted () {
    // Fetch the available products and set the initial chart data
    this.updateChart()
  }
}
</script>
