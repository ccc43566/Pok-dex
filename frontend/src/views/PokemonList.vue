<template>
  <div class="pokemon-list">
    <div class="controls">
      <div class="search-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索宝可梦名称或序号..."
          @keyup.enter="handleSearch"
        >
        <button @click="handleSearch" class="search-btn">搜索</button>
      </div>
      <div class="filters">
        <select v-model="selectedType" @change="handleTypeFilter" class="type-filter">
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
            loading="lazy"
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

    <div v-if="!loading && !error && pokemonList.length > 0 && hasMore" class="pagination">
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
      hasMore: true
    }
  },
  computed: {
    availableTypes() {
      return [
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
    // 处理类型过滤
    handleTypeFilter() {
      this.loadPokemon(true)
    },
    
    // 处理搜索
    handleSearch() {
      if (this.searchQuery.trim()) {
        this.searchPokemon()
      } else {
        this.loadPokemon(true)
      }
    },
    
    // 搜索宝可梦
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
      if (!this.hasMore || this.loading || this.loadingMore) return

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
        this.error = error.message
        console.error('加载更多宝可梦失败:', error)
      } finally {
        this.loadingMore = false
      }
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
      const safeName = pokemon.name.toLowerCase()
        .replace(/[^a-z0-9]/g, '')
        .replace(/\s+/g, '')
      return `/images/${pokemon.id}_${safeName}.gif`
    },

    handleImageError(event) {
      const img = event.target
      const src = img.src
      if (src.endsWith('.gif')) {
        img.src = src.replace('.gif', '.png')
      } else if (!img.src.includes('25_pikachu.gif')) {
        img.src = '/images/25_pikachu.gif'
        img.onerror = null
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
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
}

.search-btn {
  padding: 0.75rem 1.5rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 1rem;
}

.search-btn:hover {
  background-color: #45a049;
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.type-filter {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 120px;
}

.loading, .error, .no-results {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.error {
  color: #d32f2f;
}

.error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error button:hover {
  background-color: #45a049;
}

.pokemon-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
  width: 100%;
  box-sizing: border-box;
}

.pokemon-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 200px;
  justify-content: space-between;
}

.pokemon-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.pokemon-image {
  width: 80px;
  height: 80px;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pokemon-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.pokemon-info {
  text-align: center;
  width: 100%;
}

.pokemon-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #333;
  word-wrap: break-word;
}

.types {
  display: flex;
  justify-content: center;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.type-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.625rem;
  font-weight: bold;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.stats {
  font-size: 0.75rem;
  color: #666;
}

.pagination {
  text-align: center;
  margin: 2rem 0;
}

.load-more-btn {
  padding: 0.75rem 2rem;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background-color: #1976d2;
}

.load-more-btn:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
}

/* 属性颜色 */
.type-normal { background-color: #A8A77A; }
.type-fire { background-color: #EE8130; }
.type-water { background-color: #6390F0; }
.type-electric { background-color: #F7D02C; }
.type-grass { background-color: #7AC74C; }
.type-ice { background-color: #96D9D6; }
.type-fighting { background-color: #C22E28; }
.type-poison { background-color: #A33EA1; }
.type-ground { background-color: #E2BF65; }
.type-flying { background-color: #A98FF3; }
.type-psychic { background-color: #F95587; }
.type-bug { background-color: #A6B91A; }
.type-rock { background-color: #B6A136; }
.type-ghost { background-color: #735797; }
.type-dragon { background-color: #6F35FC; }
.type-dark { background-color: #705746; }
.type-steel { background-color: #B7B7CE; }
.type-fairy { background-color: #D685AD; }

@media (max-width: 1400px) {
  .pokemon-grid {
    grid-template-columns: repeat(6, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 1024px) {
  .pokemon-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .search-bar {
    max-width: none;
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .type-filter {
    width: 100%;
  }

  .pokemon-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .pokemon-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>
