<template>
  <div class="items-list">
    <h1>物品列表</h1>

    <!-- 搜索和过滤 -->
    <div class="filters">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索物品名称..."
        @input="debouncedSearch"
      >

      <select v-model="categoryFilter" @change="fetchItems">
        <option value="">所有类别</option>
        <option v-for="category in categories" :key="category" :value="category">
          {{ category }}
        </option>
      </select>
    </div>

    <!-- 物品网格 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="items-grid">
      <div
        v-for="item in items"
        :key="item.id"
        class="item-card"
      >
        <div class="item-header">
          <h3>{{ item.name }}</h3>
          <span class="item-id">#{{ item.id }}</span>
        </div>

        <div class="item-info">
          <p v-if="item.category" class="category">{{ item.category }}</p>
          <p v-if="item.shortDesc" class="description">{{ item.shortDesc }}</p>
        </div>

        <div class="item-details">
          <div v-if="item.english" class="english-name">{{ item.english }}</div>
          <div v-if="item.gen" class="gen">第{{ item.gen }}代</div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > limit" class="pagination">
      <button
        @click="prevPage"
        :disabled="skip === 0"
        class="page-btn"
      >
        上一页
      </button>

      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>

      <button
        @click="nextPage"
        :disabled="skip + limit >= total"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script>
import { pokemonAPI } from '../services/api.js'

export default {
  name: 'ItemsList',
  data() {
    return {
      items: [],
      loading: true,
      error: null,
      searchQuery: '',
      categoryFilter: '',
      skip: 0,
      limit: 50,
      total: 0,
      categories: [],
      searchTimeout: null
    }
  },
  computed: {
    currentPage() {
      return Math.floor(this.skip / this.limit) + 1
    },
    totalPages() {
      return Math.ceil(this.total / this.limit)
    }
  },
  methods: {
    async fetchItems() {
      this.loading = true
      this.error = null

      try {
        const params = {
          skip: this.skip,
          limit: this.limit
        }

        if (this.searchQuery) {
          params.search = this.searchQuery
        }

        if (this.categoryFilter) {
          params.category_filter = this.categoryFilter
        }

        const response = await pokemonAPI.getItems(params)
        this.items = response.items || []
        this.total = response.total || 0

        // 收集所有类别用于过滤器
        if (!this.categories.length) {
          try {
            const response = await pokemonAPI.getItemCategories()
            this.categories = response.categories || []
          } catch (err) {
            console.error('获取物品类别失败:', err)
          }
        }
      } catch (err) {
        this.error = '获取物品列表失败: ' + err.message
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.skip = 0 // 重置到第一页
        this.fetchItems()
      }, 300)
    },

    prevPage() {
      if (this.skip > 0) {
        this.skip -= this.limit
        this.fetchItems()
      }
    },

    nextPage() {
      if (this.skip + this.limit < this.total) {
        this.skip += this.limit
        this.fetchItems()
      }
    }
  },

  mounted() {
    this.fetchItems()
  }
}
</script>

<style scoped>
.items-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filters input,
.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filters input {
  flex: 1;
  min-width: 200px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.item-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.item-id {
  color: #666;
  font-size: 14px;
  font-weight: bold;
}

.category {
  color: #007bff;
  font-weight: bold;
  margin-bottom: 8px;
}

.description {
  color: #555;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 8px;
}

.item-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #777;
}

.english-name {
  font-style: italic;
}

.gen {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f8f9fa;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #dc3545;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }

  .items-grid {
    grid-template-columns: 1fr;
  }
}
</style>
