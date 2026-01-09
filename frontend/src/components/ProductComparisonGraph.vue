<template>
  <div class="graph-container">
    <div class="graph-header">
      <h3>Product Comparison</h3>
      <div class="chart-type-toggle">
        <button
          :class="{ active: chartType === 'bar' }"
          @click="chartType = 'bar'"
        >
          Bar
        </button>
        <button
          :class="{ active: chartType === 'pie' }"
          @click="chartType = 'pie'"
        >
          Pie
        </button>
      </div>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="hasData" class="chart-wrapper">
      <component :is="chartComponent" :data="formattedChartData" :options="chartOptions" />
    </div>
    <div v-else class="no-data">No product data available</div>
  </div>
</template>

<script>
import axios from 'axios'
import { Bar, Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  PieController,
  DoughnutController,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, PieController, DoughnutController, CategoryScale, LinearScale, ArcElement)

const dataLabelPlugin = {
  id: 'dataLabels',
  afterDatasetsDraw: (chart) => {
    const { ctx, data } = chart
    const chartType = chart.getDatasetMeta(0).type

    if (chartType === 'pie' || chartType === 'doughnut') {
      ctx.save()
      const datasets = data.datasets

      datasets.forEach((dataset, datasetIndex) => {
        const meta = chart.getDatasetMeta(datasetIndex)
        meta.data.forEach((arc, index) => {
          const value = dataset.data[index]

          ctx.font = 'bold 12px sans-serif'
          ctx.fillStyle = '#fff'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'

          const angle = (arc.startAngle + arc.endAngle) / 2

          const outerRadius = arc.outerRadius || 100
          const innerRadius = arc.innerRadius || 0
          const middleRadius = (outerRadius + innerRadius) / 2

          const labelX = arc.x + Math.cos(angle) * middleRadius
          const labelY = arc.y + Math.sin(angle) * middleRadius

          ctx.fillText(value, labelX, labelY)
        })
      })

      ctx.restore()
    }
  }
}

ChartJS.register(dataLabelPlugin)

export default {
  name: 'ProductComparisonGraph',
  components: {
    Bar,
    Pie
  },
  data () {
    return {
      loading: true,
      error: null,
      productDetails: [],
      chartData: null,
      chartType: 'bar'
    }
  },
  computed: {
    hasData () {
      return this.chartData && this.chartData.labels && this.chartData.labels.length > 0
    },
    chartComponent () {
      return this.chartType === 'pie'
        ? Pie
        : Bar
    },
    formattedChartData () {
      if (!this.chartData) return null

      const isPie = this.chartType === 'pie'

      if (isPie) {
        const colors = [
          '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
          '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
        ]

        return {
          labels: this.chartData.labels.map((label) => label.split(' ($')[0]),
          datasets: this.chartData.datasets.map((dataset, datasetIndex) => ({
            ...dataset,
            type: 'doughnut',
            backgroundColor: this.chartData.labels.map((_, index) => colors[index % colors.length]),
            borderColor: '#ffffff',
            borderWidth: 3,
            hoverBackgroundColor: this.chartData.labels.map((_, index) => colors[index % colors.length]),
            hoverBorderColor: '#ffffff',
            hoverOffset: 0,
            circumference: 360,
            rotation: 0,
            outerRadius: datasetIndex === 0 ? 80 : 100,
            innerRadius: datasetIndex === 0 ? 0 : 85
          }))
        }
      }

      return this.chartData
    },
    chartOptions () {
      const isPie = this.chartType === 'pie'
      return {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: isPie ? 20 : 0
        },
        animation: isPie
          ? {
              animateScale: false,
              animateRotate: false,
              duration: 0
            }
          : {
              duration: 0
            },
        interaction: {
          mode: 'nearest',
          intersect: true
        },
        hover: isPie
          ? {
              mode: 'dataset',
              intersect: false,
              animation: {
                duration: 0
              }
            }
          : {
              mode: 'nearest',
              intersect: true
            },
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
            callbacks: {
              label: (context) => {
                const productIndex = context.dataIndex
                const product = this.productDetails[productIndex]
                const value = context.raw
                if (product) {
                  return `${product.name} ($${product.price.toFixed(2)}): ${value}`
                }
                return value
              }
            }
          },
          legend: {
            position: isPie
              ? 'bottom'
              : 'top',
            labels: {
              color: '#ffffff',
              font: {
                size: 12,
                weight: 'normal'
              },
              padding: 20,
              usePointStyle: isPie,
              pointStyle: 'circle',
              generateLabels: (chart) => {
                if (isPie) {
                  const labels = []
                  const colors = ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
                  chart.data.labels.forEach((label, index) => {
                    const price = this.productDetails[index]?.price.toFixed(2) || '0.00'
                    labels.push({
                      text: `${label} ($${price})`,
                      fillStyle: colors[index % colors.length],
                      strokeStyle: '#ffffff',
                      lineWidth: 2,
                      hidden: false,
                      index: index,
                      fontColor: '#ffffff'
                    })
                  })
                  return labels
                }
                const defaultLabels = ChartJS.defaults.plugins.legend.labels.generateLabels(chart)
                return defaultLabels.map(label => ({
                  ...label,
                  fontColor: '#ffffff'
                }))
              }
            }
          }
        },
        scales: isPie
          ? {}
          : {
              x: {
                stacked: false,
                ticks: {
                  color: '#fff',
                  callback: (value, index) => {
                    const product = this.productDetails[index]
                    if (product) {
                      return product.name.length > 10
                        ? product.name.substring(0, 10) + '...'
                        : product.name
                    }
                    return ''
                  }
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
    await this.fetchData()
  },
  methods: {
    async fetchData () {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/products/comparison/')
        const data = response.data

        this.productDetails = data.product_details || []

        this.chartData = {
          labels: data.labels.map((name, index) =>
            `${name} ($${this.productDetails[index]?.price.toFixed(2) || '0.00'})`
          ),
          datasets: data.datasets.map((dataset) => ({
            ...dataset,
            borderWidth: 2,
            hoverBackgroundColor: dataset.backgroundColor.replace('0.7', '0.9'),
            hoverBorderColor: dataset.borderColor
          }))
        }
      } catch (err) {
        this.error = 'Failed to load product comparison data'
        console.error('Error fetching product comparison:', err)
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
  max-width: 1000px;
  padding: 30px 20px;
  margin-top: 40px;
}

.graph-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.graph-container h3 {
  margin: 0;
  color: #fff;
  font-size: 24px;
}

.chart-type-toggle {
  display: flex;
  gap: 8px;
}

.chart-type-toggle button {
  padding: 8px 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.chart-type-toggle button:hover {
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
}

.chart-type-toggle button.active {
  background: #42A5F5;
  border-color: #42A5F5;
  color: white;
}

.chart-wrapper {
  position: relative;
  height: 450px;
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
