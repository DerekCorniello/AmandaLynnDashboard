<template>
  <div class="center-container">
    <div class="content">
      <h1>{{ tableTitle }}</h1>

      <!-- Search bar -->
      <label>Search:</label>
      <input v-model="searchQuery" @input="handleSearch" placeholder="Search..."/><br><br>

      <!-- Sorting controls -->
      <label>Sort by:
        <select v-model="sortField" @change="fetchData">
          <option v-for="header in tableHeaders" :key="header" :value="header">{{ toTitleCase(header) }}</option>
        </select>
      </label><br><br>

      <label>Order:
        <select v-model="sortOrder" @change="fetchData">
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </label><br><br>

      <!-- Dropdown to select the table type -->
      <select v-model="selectedTable" @change="handleTableChange">
        <option value="products">Products</option>
        <option value="expenses">Expenses</option>
        <option value="transactions">Transactions</option>
      </select><br><br>

      <!-- Conditional "Show Retired Products" checkbox -->
      <label v-if="selectedTable === 'products'">
        <input
          type="checkbox"
          v-model="showRetiredFlag"
          @change="fetchData"
        />
        Show Retired Products
      </label><br><br>

      <!-- Table to display the data -->
      <table v-if="data.length">
        <thead>
          <tr>
            <th v-for="(header, index) in tableHeaders" :key="'header-' + index">{{ toTitleCase(header) }}</th>
            <th v-if="selectedTable === 'products'">Status</th> <!-- Conditional header for products only -->
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in data" :key="'item-' + index">
             <td v-for="(header, index) in tableHeaders" :key="'data-' + index">
               <template v-if="isEditing && item.id === currentEditId">
                 <input v-model="editItemData[header]" :type="getInputType(header)" />
               </template>
               <template v-else>
                 {{ header === 'name' ? toTitleCase(item[header]) : (item[header] || 'N/A') }}
               </template>
             </td>

            <!-- Retired checkbox column (visible only for products table) -->
            <td v-if="selectedTable === 'products'">
              <template v-if="isEditing && item.id === currentEditId">
                <input
                  type="checkbox"
                  v-model="editItemData.is_retired"
                />
              </template>
              <template v-else>
                {{ item.is_retired ? 'Retired' : 'Active' }}
              </template>
            </td>

            <!-- Actions column -->
            <td>
              <button v-if="isEditing && item.id === currentEditId" @click="deleteItem(item.id)">Delete</button>
              <button v-if="!isEditing && item.id !== currentEditId" @click="editItem(item)">Edit</button>
              <button v-if="isEditing && item.id === currentEditId" @click="saveEdit">Save</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No data available.</p>
    </div>
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
      showRetiredFlag: false,
      data: [],
      tableHeaders: [],
      tableTitle: 'Product List',
      isEditing: false,
      currentEditId: null,
      editItemData: {},
      searchQuery: '',
      sortField: 'name' | 'type',
      sortOrder: 'asc'
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
    handleTableChange () {
      this.isEditing = false
      this.updateSortField()
      this.fetchData()
    },
    updateSortField () {
      switch (this.selectedTable) {
        case 'products':
          this.sortField = 'name'
          break
        case 'expenses':
          this.sortField = 'type'
          break
        case 'transactions':
          this.sortField = 'type'
          break
      }
    },
    handleSearch () {
      this.fetchData()
    },
    async fetchData () {
      let endpoint = ''
      let headers = []

      switch (this.selectedTable) {
        case 'products':
          endpoint = 'http://127.0.0.1:8000/api/products/'
          headers = ['name', 'stock', 'price', 'number_sold']
          this.tableTitle = 'Product List'
          this.sortField = this.sortField || 'name'
          break
        case 'expenses':
          endpoint = 'http://127.0.0.1:8000/api/expenses/'
          headers = ['name', 'date', 'type', 'price']
          this.tableTitle = 'Expense List'
          this.sortField = this.sortField || 'name'
          break
        case 'transactions':
          endpoint = 'http://127.0.0.1:8000/api/transactions/'
          headers = ['total', 'date', 'type', 'products']
          this.tableTitle = 'Transaction List'
          this.sortField = this.sortField || 'type'
          break
        default:
          return
      }

      try {
        const response = await axios.get(endpoint, {
          params: {
            search: this.searchQuery,
            sort_by: this.sortField,
            order: this.sortOrder,
            show_retired: this.showRetiredFlag
          }
        })
        this.data = response.data.map(item => {
          const mappedItem = {}
          headers.forEach(header => {
            mappedItem[header] = item[header] !== undefined ? item[header] : 'N/A'
          })
          return {
            ...mappedItem,
            id: item.id,
            is_retired: item.is_retired
          }
        })
        this.tableHeaders = headers
      } catch (error) {
        console.error('Error fetching data:', error)
        this.data = []
        this.tableHeaders = []
      }
    },
    async deleteItem (id) {
      try {
        if (confirm("Are you sure you'd like to delete this item?")) {
          await axios.delete(`http://127.0.0.1:8000/api/${this.selectedTable}/delete/${id}/`)
          this.isEditing = false
          this.currentEditId = null
          this.editItemData = {}
        }
        this.fetchData()
      } catch (error) {
        console.error('Error deleting item:', error)
      }
    },
    editItem (item) {
      this.isEditing = true
      this.currentEditId = item.id
      this.editItemData = {}
      this.tableHeaders.forEach(header => {
        this.editItemData[header] = item[header] !== undefined ? item[header] : 'N/A'
      })
      this.editItemData.is_retired = item.is_retired
    },
    async saveEdit () {
      try {
        const endpoint = `http://127.0.0.1:8000/api/${this.selectedTable}/update/${this.currentEditId}/`
        await axios.put(endpoint, this.editItemData)
        this.isEditing = false
        this.currentEditId = null
        this.fetchData()
      } catch (error) {
        console.error('Error updating item:', error)
      }
    },
    getInputType (header) {
      return header === 'price' || header === 'total' ? 'number' : 'text'
    }
  },
  created () {
    this.updateSortField()
    this.fetchData()
  },
  watch: {
    selectedTable () {
      this.fetchData()
    }
  }
}
</script>
