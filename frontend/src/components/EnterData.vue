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

        <!-- Typeahead Input for Expense Name -->
        <input
          type="text"
          v-model="newEntry.name"
          @input="updateSuggestions"
          @blur="hideSuggestions"
          @focus="updateSuggestions"
          placeholder="Enter expense name"
          required
        />
         <ul v-if="showSuggestions" class="suggestions-list">
           <li v-for="suggestion in filteredSuggestions" :key="suggestion" @mousedown="selectSuggestion(suggestion)">
             {{ toTitleCase(suggestion) }}
           </li>
         </ul><br>

        <label for="date">Date:</label><br>
        <input type="date" v-model="newEntry.date" required /><br>

        <label for="type">Type:</label><br>
        <input type="text" v-model="newEntry.type" required /><br>

        <label for="price">Price:</label><br>
        <input type="number" step="0.01" v-model="newEntry.price" required /><br>
      </div>

      <div v-if="selectedTable === 'transactions'">
        <div v-for="(product, index) in productsList" :key="index" class="product-entry">
          <div class="product-row">
            <label style="margin-bottom: 0px;" for="product-select">Product:</label>
             <select v-model="product.name" @change="updateProductCount(index)" class="product-select">
               <option v-for="productName in availableProducts" :key="productName" :value="productName">
                 {{ toTitleCase(productName) }}
               </option>
             </select>

            <label style="margin-bottom: 0px;" for="product-count">Count:</label>
            <input type="number" v-model="product.count" min="1" required class="product-count" />

            <button type="button" @click="removeProductEntry(index)" class="remove-btn">Remove</button>
          </div>
        </div><br>

        <div class="product-actions">
          <button type="button" @click="addProductEntry" class="add-btn">Add Another Product</button>
        </div><br><br>

        <label for="total">Total:</label><br>
        <input type="number" step="0.01" v-model="newEntry.total" required /><br>

        <label for="date">Date:</label><br>
        <input type="date" v-model="newEntry.date" required /><br>

        <label for="type">Type:</label><br>
        <input type="text" v-model="newEntry.type" required /><br>
      </div>

      <button type="submit">Add Entry</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
import titleCaseMixin from '../mixins/titleCaseMixin'

export default {
  mixins: [titleCaseMixin],
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
      },
      expenseNames: [], // Store list of names from API here
      showSuggestions: false, // Controls visibility of suggestions list
      filteredSuggestions: [], // Holds matching suggestions as user types
      productsList: [
        { name: '', count: 1 }
      ],
      availableProducts: [] // This will be populated with product names from your API
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
    toTitleCase (str) {
      if (!str) return ''
      if (typeof str !== 'string') return str
      // Replace underscores with spaces first
      str = str.replace(/_/g, ' ')
      // Then apply title case
      return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
    },
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
        case 'transactions': {
          endpoint = 'http://127.0.0.1:8000/api/transactions/create/'
          const productsArray = []
          this.productsList.forEach(product => {
            for (let i = 0; i < product.count; i++) {
              productsArray.push(product.name)
            }
          })
          data = {
            total: this.newEntry.total,
            date: this.newEntry.date,
            type: this.newEntry.type,
            products: productsArray.join(',')
          }
          break
        }
        default:
          return
      }

      try {
        await axios.post(endpoint, data)
        this.resetForm() // Clear the form

        // Emit an event or call a method to update the chart/table data
        this.$emit('data-updated', this.selectedTable) // Emitting an event to parent component
        await this.getExpenseNames()
        await this.getAvailableProducts()
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
        date: todayDate,
        type: this.selectedTable === 'expenses' ? 'Fee' : this.selectedTable === 'transactions' ? 'Purchase' : '',
        total: null,
        products: ''
      }

      this.productsList = [{ name: '', count: 1 }]
    },

    getTodayDate () {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },

    async getExpenseNames () {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/expenses/')
        this.expenseNames = response.data.map(item => item.name)
      } catch (error) {
        console.error('Error fetching Expense Names for EnterData: ', error)
      }
    },

    updateSuggestions () {
      const input = this.newEntry.name.toLowerCase()
      this.filteredSuggestions = this.expenseNames.filter(name => name.toLowerCase().includes(input))
      this.showSuggestions = this.filteredSuggestions.length > 0
    },

    selectSuggestion (suggestion) {
      this.newEntry.name = suggestion
      this.showSuggestions = false
    },

    hideSuggestions () {
      setTimeout(() => {
        this.showSuggestions = false
      }, 200)
    },
    addProductEntry () {
      this.productsList.push({ name: '', count: 1 })
    },
    removeProductEntry (index) {
      this.productsList.splice(index, 1)
    },
    updateProductCount () {
      // This can trigger any additional logic if necessary, e.g., updating totals
    },
    async getAvailableProducts () {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/products/')
        this.availableProducts = response.data.map(item => item.name)
      } catch (error) {
        console.error('Error fetching available products:', error)
      }
    }
  },
  async mounted () {
    this.resetForm()
    await this.getExpenseNames()
    await this.getAvailableProducts()
  }
}
</script>

<style scoped>
.suggestions-list {
  list-style-type: none;
  margin: 0;
  padding: 0;
  border: 1px solid #ccc;
  max-height: 100px;
  overflow-y: auto;
  background-color: #3a294b;
}

.suggestions-list li {
  padding: 8px;
  cursor: pointer;
}

.suggestions-list li:hover {
  background-color: #8151a1;
}

.product-entry {
  display: flex;
  justify-content: center;
}

.product-row {
  display: flex;
  align-items: center;
  gap: 2%;
  width: 80%;
}

.product-select {
  width: 30%;
}

.product-count {
  width: 10%;
  text-align: center;
}

.product-actions {
  text-align: center;
}
</style>
