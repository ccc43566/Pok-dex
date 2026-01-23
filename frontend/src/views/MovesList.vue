<template>
  <div class="moves-list">
    <h1>技能列表</h1>

    <!-- 搜索和过滤 -->
    <div class="filters">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索技能名称..."
        @input="debouncedSearch"
      >

      <select v-model="typeFilter" @change="fetchMoves">
        <option value="">所有属性</option>
        <option v-for="type in moveTypes" :key="type" :value="type">
          {{ type }}
        </option>
      </select>

      <select v-model="categoryFilter" @change="fetchMoves">
        <option value="">所有类别</option>
        <option v-for="category in moveCategories" :key="category" :value="category">
          {{ category }}
        </option>
      </select>
    </div>

    <!-- 技能网格 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="moves-grid">
      <div
        v-for="move in moves"
        :key="move.id"
        class="move-card"
      >
        <div class="move-header">
          <h3>{{ move.name }}</h3>
          <span class="move-id">#{{ move.id }}</span>
        </div>

        <div class="move-info">
          <div v-if="move.type" class="type" :class="`type-${move.type.toLowerCase()}`">
            {{ move.type }}
          </div>
          <div v-if="move.category" class="category">
            {{ move.category }}
          </div>
        </div>

        <div class="move-stats">
          <div v-if="move.power !== null && move.power !== undefined" class="stat">
            <span class="stat-label">威力:</span>
            <span class="stat-value">{{ move.power || '-' }}</span>
          </div>
          <div v-if="move.accuracy !== null && move.accuracy !== undefined" class="stat">
            <span class="stat-label">命中:</span>
            <span class="stat-value">{{ move.accuracy }}%</span>
          </div>
          <div v-if="move.pp" class="stat">
            <span class="stat-label">PP:</span>
            <span class="stat-value">{{ move.pp }}</span>
          </div>
        </div>

        <div v-if="move.shortDesc" class="description">
          {{ move.shortDesc }}
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
  name: 'MovesList',
  data() {
    return {
      moves: [],
      loading: true,
      error: null,
      searchQuery: '',
      typeFilter: '',
      categoryFilter: '',
      skip: 0,
      limit: 50,
      total: 0,
      moveTypes: [],
      moveCategories: [],
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
    async fetchMoves() {
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

        if (this.typeFilter) {
          params.type_filter = this.typeFilter
        }

        if (this.categoryFilter) {
          params.category_filter = this.categoryFilter
        }

        const response = await pokemonAPI.getMoves(params)
        this.moves = response.moves || []
        this.total = response.total || 0

        // 收集所有类型和类别用于过滤器
        if (!this.moveTypes.length || !this.moveCategories.length) {
          try {
            const response = await pokemonAPI.getMoveFilters()
            this.moveTypes = response.types || []
            this.moveCategories = response.categories || []
          } catch (err) {
            console.error('获取技能过滤选项失败:', err)
          }
        }
      } catch (err) {
        this.error = '获取技能列表失败: ' + err.message
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.skip = 0 // 重置到第一页
        this.fetchMoves()
      }, 300)
    },

    prevPage() {
      if (this.skip > 0) {
        this.skip -= this.limit
        this.fetchMoves()
      }
    },

    nextPage() {
      if (this.skip + this.limit < this.total) {
        this.skip += this.limit
        this.fetchMoves()
      }
    }
  },

  mounted() {
    this.fetchMoves()
  }
}
</script>

<style scoped>
.moves-list {
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

.moves-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.move-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.move-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.move-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.move-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.move-id {
  color: #666;
  font-size: 14px;
  font-weight: bold;
}

.move-info {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.type {
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.category {
  padding: 4px 8px;
  border-radius: 4px;
  background: #f8f9fa;
  color: #333;
  font-size: 12px;
  font-weight: bold;
}

/* 技能属性颜色 */
.type-normal { background: #A8A878; }
.type-fire { background: #F08030; }
.type-water { background: #6890F0; }
.type-electric { background: #F8D030; }
.type-grass { background: #78C850; }
.type-ice { background: #98D8D8; }
.type-fighting { background: #C03028; }
.type-poison { background: #A040A0; }
.type-ground { background: #E0C068; }
.type-flying { background: #A890F0; }
.type-psychic { background: #F85888; }
.type-bug { background: #A8B820; }
.type-rock { background: #B8A038; }
.type-ghost { background: #705898; }
.type-dragon { background: #7038F8; }
.type-dark { background: #705848; }
.type-steel { background: #B8B8D0; }
.type-fairy { background: #EE99AC; }

.move-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f8f9fa;
  padding: 6px 10px;
  border-radius: 4px;
  min-width: 60px;
}

.stat-label {
  font-size: 11px;
  color: #666;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.description {
  font-size: 14px;
  color: #555;
  line-height: 1.4;
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

  .moves-grid {
    grid-template-columns: 1fr;
  }

  .move-stats {
    justify-content: center;
  }
}
</style>
