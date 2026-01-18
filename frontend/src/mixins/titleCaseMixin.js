export default {
  methods: {
    toTitleCase (str) {
      if (!str) return ''
      if (typeof str !== 'string') return str
      return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
    }
  }
}
