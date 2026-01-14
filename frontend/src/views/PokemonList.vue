<template>
  <div class="pokemon-list">
    <div class="controls">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索宝可梦名称..."
          @keyup.enter="handleSearch"
        >
        <button @click="handleSearch" :disabled="loading">搜索</button>
      </div>

      <div class="filters">
        <select v-model="selectedType" @change="handleTypeFilter">
          <option value="">所有属性</option>
          <option v-for="type in availableTypes" :key="type" :value="type">
            {{ type }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadPokemon">重试</button>
    </div>

    <div v-else class="pokemon-grid">
      <div
        v-for="pokemon in pokemonList"
        :key="pokemon.id"
        class="pokemon-card"
        @click="goToDetail(pokemon.id)"
      >
        <div class="pokemon-image">
          <img
            :src="getPokemonImage(pokemon)"
            :alt="pokemon.name"
            @error="handleImageError"
          >
        </div>
        <div class="pokemon-info">
          <h3>#{{ pokemon.id }} {{ pokemon.name }}</h3>
          <div class="types">
            <span
              v-for="type in getPokemonTypes(pokemon)"
              :key="type"
              class="type-badge"
              :class="`type-${type.toLowerCase()}`"
            >
              {{ type }}
            </span>
          </div>
          <div class="stats" v-if="pokemon.total">
            <span>总种族值: {{ pokemon.total }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !error && pokemonList.length > 0" class="pagination">
      <button
        @click="loadMore"
        :disabled="loadingMore"
        class="load-more-btn"
      >
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <div v-if="!loading && pokemonList.length === 0" class="no-results">
      <p>未找到匹配的宝可梦</p>
    </div>
  </div>
</template>

<script>
import { pokemonAPI } from '@/services/api.js'

export default {
  name: 'PokemonList',
  data() {
    return {
      pokemonList: [],
      loading: true,
      loadingMore: false,
      error: null,
      searchQuery: '',
      selectedType: '',
      skip: 0,
      limit: 50,
      hasMore: true,
      availableTypes: [
        'Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Fighting',
        'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost',
        'Dragon', 'Dark', 'Steel', 'Fairy'
      ]
    }
  },
  mounted() {
    this.loadPokemon()
  },
  methods: {
    async loadPokemon(reset = false) {
      if (reset) {
        this.skip = 0
        this.pokemonList = []
        this.hasMore = true
      }

      this.loading = true
      this.error = null

      try {
        const params = {
          skip: this.skip,
          limit: this.limit
        }

        if (this.selectedType) {
          params.type_filter = this.selectedType
        }

        const data = await pokemonAPI.getPokemon(params)
        this.pokemonList = reset ? data : [...this.pokemonList, ...data]

        if (data.length < this.limit) {
          this.hasMore = false
        }
      } catch (error) {
        this.error = error.message
        console.error('加载宝可梦失败:', error)
      } finally {
        this.loading = false
      }
    },

    async loadMore() {
      if (!this.hasMore || this.loadingMore) return

      this.loadingMore = true
      this.skip += this.limit

      try {
        const params = {
          skip: this.skip,
          limit: this.limit
        }

        if (this.selectedType) {
          params.type_filter = this.selectedType
        }

        const data = await pokemonAPI.getPokemon(params)
        this.pokemonList = [...this.pokemonList, ...data]

        if (data.length < this.limit) {
          this.hasMore = false
        }
      } catch (error) {
        console.error('加载更多宝可梦失败:', error)
        this.skip -= this.limit // 回滚skip
      } finally {
        this.loadingMore = false
      }
    },

    handleSearch() {
      if (this.searchQuery.trim()) {
        this.searchPokemon()
      } else {
        this.loadPokemon(true)
      }
    },

    async searchPokemon() {
      this.loading = true
      this.error = null

      try {
        const result = await pokemonAPI.searchPokemon(this.searchQuery.trim())
        this.pokemonList = result.results || []
        this.hasMore = false
      } catch (error) {
        this.error = error.message
        console.error('搜索宝可梦失败:', error)
      } finally {
        this.loading = false
      }
    },

    handleTypeFilter() {
      this.loadPokemon(true)
    },

    goToDetail(id) {
      this.$router.push(`/pokemon/${id}`)
    },

    getPokemonTypes(pokemon) {
      const types = []
      if (pokemon.type1) types.push(pokemon.type1)
      if (pokemon.type2) types.push(pokemon.type2)
      return types
    },

    getPokemonImage(pokemon) {
      // 优先使用数据库中的image_path，如果没有则生成路径
      if (pokemon.image_path) {
        // 从image_path中提取文件名
        const pathParts = pokemon.image_path.split(/[/\\]/)
        const filename = pathParts[pathParts.length - 1]
        return `/images/${filename}`
      } else {
        // 生成默认路径，清理名字中的特殊字符
        const safeName = pokemon.name.toLowerCase()
          .replace(/[^a-z0-9]/g, '') // 只保留字母和数字
          .replace(/\s+/g, '') // 移除空格
        return `/images/${pokemon.id}_${safeName}.gif`
      }
    },

    handleImageError(event) {
      // 使用默认图片，但只在真正需要时
      const img = event.target
      if (!img.src.includes('25_pikachu.gif')) {
        // 如果不是已经在显示默认图片，则显示默认图片
        img.src = '/images/25_pikachu.gif'
        img.onerror = null // 防止无限循环
      }
    }
  }
}
</script>

<style scoped>
.pokemon-list {
  max-width: 1400px;
  margin: 0 auto;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 2rem;
}

.search-bar {
  display: flex;
  flex: 1;
  max-width: 400px;
}

.search-bar input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 5px 0 0 5px;
  font-size: 1rem;
}

.search-bar button {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0 5px 5px 0;
  cursor: pointer;
  font-size: 1rem;
}

.search-bar button:hover:not(:disabled) {
  background: #5a67d8;
}

.search-bar button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.filters select {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  min-width: 150px;
}

.pokemon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.pokemon-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.pokemon-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}

.pokemon-image {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.pokemon-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.pokemon-info {
  padding: 1rem;
}

.pokemon-info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
}

.types {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.type-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  text-transform: uppercase;
}

/* 属性颜色 */
.type-normal { background: #A8A878; }
.type-fire { background: #F08030; }
.type-water { background: #6890F0; }
.type-grass { background: #78C850; }
.type-electric { background: #F8D030; }
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

.stats {
  font-size: 0.9rem;
  color: #666;
}

.loading, .error, .no-results {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
}

.error {
  color: #e74c3c;
}

.error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.pagination {
  text-align: center;
  margin-top: 2rem;
}

.load-more-btn {
  padding: 1rem 2rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.load-more-btn:hover:not(:disabled) {
  background: #5a67d8;
}

.load-more-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-bar {
    max-width: none;
  }

  .pokemon-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
}
</style>
