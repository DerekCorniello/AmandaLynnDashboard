<template>
  <div>
    <h2 style="text-align: center;">Add New Entry to {{ selectedTableTitle }}</h2>

    <!-- Dropdown to select the table type -->
    <select v-model="selectedTable" @change="resetForm">
      <option value="products">Products</option>
      <option value="expenses">Expenses</option>
      <option value="transactions">Transactions</option>
    </select> <br> <br> <br>

    <!-- Form to add new entry -->
    <form @submit.prevent="submitForm">
      <div v-if="selectedTable === 'products'">
        <label for="name">Name:</label><br>
        <input type="text" v-model="newEntry.name" required /><br>

        <label for="stock">Stock:</label><br>
        <input type="number" v-model="newEntry.stock" required /><br>

        <label for="price">Price:</label><br>
        <input type="number" step="0.01" v-model="newEntry.price" required /><br>

        <label for="number_sold">Number Sold:</label><br>
        <input type="number" v-model="newEntry.number_sold" required /><br>
      </div>

      <div v-if="selectedTable === 'expenses'">
        <label for="name">Name:</label><br>
        <input type="text" v-model="newEntry.name" required /><br>

        <label for="date">Date:</label><br>
        <input type="date" v-model="newEntry.date" required /><br>

        <label for="type">Type:</label><br>
        <input type="text" v-model="newEntry.type" required /><br>

        <label for="price">Price:</label><br>
        <input type="number" step="0.01" v-model="newEntry.price" required /><br>
      </div>

      <div v-if="selectedTable === 'transactions'">
        <label for="total">Total:</label><br>
        <input type="number" step="0.01" v-model="newEntry.total" required /><br>

        <label for="date">Date:</label><br>
        <input type="date" v-model="newEntry.date" required /><br>

        <label for="type">Type:</label><br>
        <input type="text" v-model="newEntry.type" required /><br>

        <!-- Handle products separately for transactions -->
        <label for="products">Products (Comma-separated Names):</label><br>
        <input type="text" v-model="newEntry.products" /><br>
      </div>

      <button type="submit">Add Entry</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      selectedTable: 'products',
      newEntry: {
        name: '',
        stock: null,
        price: null,
        number_sold: null,
        date: '', // Will be set in resetForm method
        type: '',
        total: null,
        products: ''
      }
    }
  },
  computed: {
    selectedTableTitle () {
      switch (this.selectedTable) {
        case 'products':
          return 'Product'
        case 'expenses':
          return 'Expense'
        case 'transactions':
          return 'Transaction'
        default:
          return ''
      }
    }
  },
  methods: {
    async submitForm () {
      let endpoint = ''
      let data = {}

      switch (this.selectedTable) {
        case 'products':
          endpoint = 'http://127.0.0.1:8000/api/products/create/'
          data = { ...this.newEntry }
          break
        case 'expenses':
          endpoint = 'http://127.0.0.1:8000/api/expenses/create/'
          data = { ...this.newEntry }
          break
        case 'transactions':
          endpoint = 'http://127.0.0.1:8000/api/transactions/create/'
          data = {
            total: this.newEntry.total,
            date: this.newEntry.date,
            type: this.newEntry.type,
            products: this.newEntry.products.split(',').map(id => id.trim())
          }
          break
        default:
          return
      }

      try {
        await axios.post(endpoint, data)
        this.resetForm() // Clear the form

        // Emit an event or call a method to update the chart/table data
        this.$emit('data-updated', this.selectedTable) // Emitting an event to parent component
      } catch (error) {
        console.error('Error adding entry:', error)
      }
    },
    resetForm () {
      const todayDate = this.getTodayDate()
      this.newEntry = {
        name: '',
        stock: null,
        price: null,
        number_sold: null,
        date: todayDate, // Set today's date
        type: this.selectedTable === 'expenses' ? 'Fee' : this.selectedTable === 'transactions' ? 'Purchase' : '',
        total: null,
        products: ''
      }
    },

    getTodayDate () {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  },
  mounted () {
    this.resetForm() // Initialize the form with today's date
  }
}
</script>
