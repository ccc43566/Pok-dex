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

    <div class="generation-filter">
      <div class="generation-dropdown">
        <div
          class="generation-dropdown-header"
          @click="toggleGenerationDropdown"
        >
          <div class="generation-name">
            {{ selectedGeneration ? `第${selectedGeneration}世代` : '选择世代' }}
          </div>
          <div v-if="selectedGeneration" class="generation-sprites">
            <div
              v-for="example in generations.find(gen => gen.id === selectedGeneration).examples"
              :key="example.id"
              class="generation-sprite"
              :style="{ backgroundImage: `url(${getPokemonImage(example, true)})` }"
              :title="example.name"
            ></div>
          </div>
          <div v-if="selectedGeneration" class="generation-range">
            #{{ generations.find(gen => gen.id === selectedGeneration).startId }}-
            {{ generations.find(gen => gen.id === selectedGeneration).endId }}
          </div>
          <div class="dropdown-arrow" :class="{ open: isDropdownOpen }">▼</div>
        </div>
        <div
          class="generation-dropdown-menu"
          :class="{ open: isDropdownOpen }"
        >
          <div
            v-for="gen in generations"
            :key="gen.id"
            class="generation-tab"
            :class="{ active: selectedGeneration === gen.id }"
            @click="handleGenerationFilter(gen.id)"
          >
            <div class="generation-header">
              <div class="generation-name">第{{ gen.id }}世代</div>
              <div class="generation-sprites">
                <div
                  v-for="example in gen.examples"
                  :key="example.id"
                  class="generation-sprite"
                  :style="{ backgroundImage: `url(${getPokemonImage(example, true)})` }"
                  :title="example.name"
                ></div>
              </div>
              <div class="generation-range">#{{ gen.startId }}-{{ gen.endId }}</div>
            </div>
          </div>
        </div>
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
      selectedGeneration: null,
      skip: 0,
      limit: 50,
      hasMore: true,
      isDropdownOpen: false,
      availableTypes: [
        'Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Fighting',
        'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost',
        'Dragon', 'Dark', 'Steel', 'Fairy'
      ],
      generations: [
        { id: 1, startId: 1, endId: 151, examples: [{ id: 1, name: 'Bulbasaur' }, { id: 4, name: 'Charmander' }, { id: 7, name: 'Squirtle' }] },
        { id: 2, startId: 152, endId: 251, examples: [{ id: 152, name: 'Chikorita' }, { id: 155, name: 'Cyndaquil' }, { id: 158, name: 'Totodile' }] },
        { id: 3, startId: 252, endId: 386, examples: [{ id: 252, name: 'Treecko' }, { id: 255, name: 'Torchic' }, { id: 258, name: 'Mudkip' }] },
        { id: 4, startId: 387, endId: 493, examples: [{ id: 387, name: 'Turtwig' }, { id: 390, name: 'Chimchar' }, { id: 393, name: 'Piplup' }] },
        { id: 5, startId: 494, endId: 649, examples: [{ id: 495, name: 'Snivy' }, { id: 498, name: 'Tepig' }, { id: 501, name: 'Oshawott' }] },
        { id: 6, startId: 650, endId: 721, examples: [{ id: 650, name: 'Chespin' }, { id: 653, name: 'Fennekin' }, { id: 656, name: 'Froakie' }] },
        { id: 7, startId: 722, endId: 809, examples: [{ id: 722, name: 'Rowlet' }, { id: 725, name: 'Litten' }, { id: 728, name: 'Popplio' }] },
        { id: 8, startId: 810, endId: 905, examples: [{ id: 810, name: 'Grookey' }, { id: 813, name: 'Scorbunny' }, { id: 816, name: 'Sobble' }] },
        { id: 9, startId: 906, endId: 1025, examples: [{ id: 906, name: 'Sprigatito' }, { id: 909, name: 'Fuecoco' }, { id: 912, name: 'Quaxly' }] }
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

        if (this.selectedGeneration) {
          params.generation = this.selectedGeneration
        }

        if (this.selectedGeneration) {
          params.generation = this.selectedGeneration
        }

        if (this.selectedGeneration) {
          params.generation = this.selectedGeneration
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

        if (this.selectedGeneration) {
          params.generation = this.selectedGeneration
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

    toggleGenerationDropdown() {
      console.log('toggleGenerationDropdown called, current isDropdownOpen:', this.isDropdownOpen)
      this.isDropdownOpen = !this.isDropdownOpen
      console.log('After toggle, isDropdownOpen:', this.isDropdownOpen)
    },

    handleGenerationFilter(generationId) {
      this.selectedGeneration = this.selectedGeneration === generationId ? null : generationId
      this.isDropdownOpen = false // 选择后关闭下拉框
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

    getPokemonImage(pokemon, isGenerationSelector = false) {
      // 世代选择器中的御三家使用PNG，其他都使用GIF
      const safeName = pokemon.name.toLowerCase()
        .replace(/[^a-z0-9]/g, '') // 只保留字母和数字
        .replace(/\s+/g, '') // 移除空格

      console.log('getPokemonImage called with:', {
        pokemon: pokemon,
        isGenerationSelector: isGenerationSelector,
        safeName: safeName
      })

      if (isGenerationSelector) {
        // 世代选择器中的宝可梦使用PNG
        const pngPath = `/png-images/${pokemon.id}_${safeName}.png`
        console.log('Generation selector PNG path:', pngPath)
        return pngPath
      } else {
        // 所有展示页面都使用GIF（如果有的话）
        const gifPath = `/images/${pokemon.id}_${safeName}.gif`
        console.log('Regular GIF path:', gifPath)
        return gifPath
      }
    },

    handleImageError(event) {
      // 首先尝试加载PNG版本，如果失败则显示默认图片
      const img = event.target
      const src = img.src
      if (src.endsWith('.gif')) {
        // 如果是GIF图片加载失败，尝试加载PNG版本
        img.src = src.replace('.gif', '.png')
      } else if (!img.src.includes('25_pikachu.gif')) {
        // 如果已经是PNG或其他格式，且不是默认图片，则显示默认图片
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

.generation-filter {
  margin-bottom: 2rem;
}

.generation-dropdown {
  position: relative;
  max-width: 100%;
}

.generation-dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 10px;
  cursor: pointer;
  background: white;
  transition: all 0.3s ease;
}

.generation-dropdown-header:hover {
  border-color: #667eea;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.generation-dropdown-menu {
  position: absolute;
  top: calc(100% + 5px);
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.generation-dropdown-menu.open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-arrow {
  margin-left: 1rem;
  transition: transform 0.3s ease;
  color: #667eea;
  font-size: 0.8rem;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.generation-tab {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.generation-tab:last-child {
  border-bottom: none;
  border-radius: 0 0 8px 8px;
}

.generation-tab:first-child {
  border-radius: 8px 8px 0 0;
}

.generation-tab:hover {
  background: #f0f2ff;
}

.generation-tab.active {
  background: #e8ecff;
  border-left: 4px solid #667eea;
}

.generation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.generation-name {
  font-weight: bold;
  font-size: 1rem;
  color: #333;
  min-width: 80px;
}

.generation-sprites {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-grow: 1;
  align-items: center;
  height: 114px;
  min-height: 114px;
}

.generation-sprite {
  width: 110px;
  height: 110px;
  min-width: 110px;
  min-height: 110px;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  display: inline-block;
  transition: all 0.3s ease;
  border-radius: 5px;
  background-color: rgba(240, 240, 240, 0.5);
}

.generation-range {
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
  min-width: 100px;
  text-align: right;
}

.pokemon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
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
  height: 100px;
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
  padding: 0.5rem;
}

.pokemon-info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 0.9rem;
  text-align: center;
}

.types {
  display: flex;
  gap: 0.3rem;
  margin-bottom: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.type-badge {
  padding: 0.15rem 0.35rem;
  border-radius: 10px;
  font-size: 0.65rem;
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
  font-size: 0.7rem;
  color: #666;
  text-align: center;
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
