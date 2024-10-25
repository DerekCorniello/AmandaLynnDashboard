<template>
  <div>
    <h2>Expenses vs Income vs Revenue</h2>

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
import axios from 'axios'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

export default {
  components: {
    LineChart: Line
  },
  data () {
    return {
      selectedTimeScale: 'month',
      chartData: {
        labels: [], // Dates for the x-axis
        datasets: [
          {
            label: 'Expenses',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            data: [] // Expenses data
          },
          {
            label: 'Income',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            data: [] // Income data
          },
          {
            label: 'Revenue',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            data: [] // Revenue data
          }
        ]
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
    async updateChart () {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/graphdata', {
          timescale: this.selectedTimeScale, // Pass the selected time scale
          graph: 'money' // Literal 'money' labeled as 'graph'
        })

        // Assuming the response contains the data needed for the chart
        const data = response.data

        // Update the chartData with the received data
        this.chartData.labels = data.labels // Dates for x-axis
        this.chartData.datasets[0].data = data.expenses // Expenses data
        this.chartData.datasets[1].data = data.income // Income data
        this.chartData.datasets[2].data = data.revenue // Revenue data
      } catch (error) {
        console.error('Error fetching chart data:', error)
      }
    }
  },
  mounted () {
    this.updateChart() // Initial chart update
  }
}
</script>
