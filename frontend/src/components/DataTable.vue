<template>
  <div class="center-container">
    <div class="content">
      <h1>{{ tableTitle }}</h1>

      <!-- Search bar -->
      <label>Search:</label>
      <input v-model="searchQuery" @input="handleSearch" placeholder="Search..."/><br> <br>

      <!-- Sorting controls -->
      <label>Sort by:
        <select v-model="sortField" @change="fetchData">
          <option v-for="header in tableHeaders" :key="header" :value="header">{{ header }}</option>
        </select>
      </label> <br> <br>

      <label>Order:
        <select v-model="sortOrder" @change="fetchData">
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </label> <br> <br>

      <!-- Dropdown to select the table type -->
      <select v-model="selectedTable" @change="handleTableChange">
        <option value="products">Products</option>
        <option value="expenses">Expenses</option>
        <option value="transactions">Transactions</option>
      </select> <br> <br>

      <!-- Table to display the data -->
      <table v-if="data.length">
        <thead>
          <tr>
            <th v-for="(header, index) in tableHeaders" :key="'header-' + index">{{ header }}</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in data" :key="'item-' + index">
            <td v-for="(header, index) in tableHeaders" :key="'data-' + index">
              <!-- Show input fields if editing the item, otherwise show data -->
              <template v-if="isEditing && item.id === currentEditId">
                <input v-model="editItemData[header]" :type="getInputType(header)" />
              </template>
              <template v-else>
                {{ item[header] || 'N/A' }}
              </template>
            </td>
            <td>
              <button v-if="!isEditing && item.id !== currentEditId" @click="deleteItem(item.id)">Delete</button>
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

export default {
  data () {
    return {
      selectedTable: 'products',
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
    handleTableChange () {
      this.isEditing = false
      this.fetchData()
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
          this.sortField = this.sortField === 'type' ? 'name' : this.sortField
          break
        case 'expenses':
          endpoint = 'http://127.0.0.1:8000/api/expenses/'
          headers = ['name', 'date', 'type', 'price']
          this.tableTitle = 'Expense List'
          this.sortField = this.sortField === 'type' ? 'name' : this.sortField
          break
        case 'transactions':
          endpoint = 'http://127.0.0.1:8000/api/transactions/'
          headers = ['total', 'date', 'type', 'products']
          this.tableTitle = 'Transaction List'
          this.sortField = 'type'
          break
        default:
          return
      }

      try {
        const response = await axios.get(endpoint, {
          params: {
            search: this.searchQuery,
            sort_by: this.sortField,
            order: this.sortOrder
          }
        })
        this.data = response.data.map(item => {
          const mappedItem = {}
          headers.forEach(header => {
            mappedItem[header] = item[header] !== undefined ? item[header] : 'N/A'
          })
          return {
            ...mappedItem,
            id: item.id // Include id for editing and deletion
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
        await axios.delete(`http://127.0.0.1:8000/api/${this.selectedTable}/delete/${id}/`)
        this.fetchData() // Refresh data after deletion
      } catch (error) {
        console.error('Error deleting item:', error)
      }
    },
    editItem (item) {
      this.isEditing = true
      this.currentEditId = item.id
      this.editItemData = { ...item }
    },
    async saveEdit () {
      try {
        const endpoint = `http://127.0.0.1:8000/api/${this.selectedTable}/update/${this.currentEditId}/`
        await axios.put(endpoint, this.editItemData)
        this.isEditing = false
        this.currentEditId = null
        this.fetchData() // Refresh data after saving
      } catch (error) {
        console.error('Error updating item:', error)
      }
    },
    getInputType (header) {
      return header === 'price' || header === 'total' ? 'number' : 'text'
    }
  },
  created () {
    this.fetchData()
  },
  watch: {
    selectedTable () {
      this.fetchData()
    }
  }
}
</script>
