<template>
  <div class="pokemon-detail" v-if="pokemon">
    <div class="detail-header">
      <button @click="goBack" class="back-btn">← 返回列表</button>
      <h1>#{{ pokemon.id }} {{ pokemon.name }}</h1>
    </div>

    <div class="detail-content">
      <div class="pokemon-image-section">
        <div class="pokemon-image">
          <img
            :src="getPokemonImage(pokemon)"
            :alt="pokemon.name"
            @error="handleImageError"
          >
        </div>
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
      </div>

      <div class="pokemon-info-section">
        <div class="info-card">
          <h2>基本信息</h2>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">中文名:</span>
              <span class="value">{{ pokemon.name }}</span>
            </div>
            <div class="info-item" v-if="pokemon.en_name">
              <span class="label">英文名:</span>
              <span class="value">{{ pokemon.en_name }}</span>
            </div>
            <div class="info-item" v-if="pokemon.jp_name">
              <span class="label">日文名:</span>
              <span class="value">{{ pokemon.jp_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">宝可梦编号:</span>
              <span class="value">#{{ pokemon.id }}</span>
            </div>
          </div>
        </div>

        <div class="info-card" v-if="hasStats">
          <h2>种族值</h2>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">HP</span>
              <span class="stat-value">{{ pokemon.hp || 0 }}</span>
              <div class="stat-bar">
                <div class="stat-fill" :style="{ width: getStatPercentage(pokemon.hp) }"></div>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-label">攻击</span>
              <span class="stat-value">{{ pokemon.attack || 0 }}</span>
              <div class="stat-bar">
                <div class="stat-fill" :style="{ width: getStatPercentage(pokemon.attack) }"></div>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-label">防御</span>
              <span class="stat-value">{{ pokemon.defense || 0 }}</span>
              <div class="stat-bar">
                <div class="stat-fill" :style="{ width: getStatPercentage(pokemon.defense) }"></div>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-label">特攻</span>
              <span class="stat-value">{{ pokemon.sp_atk || 0 }}</span>
              <div class="stat-bar">
                <div class="stat-fill" :style="{ width: getStatPercentage(pokemon.sp_atk) }"></div>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-label">特防</span>
              <span class="stat-value">{{ pokemon.sp_def || 0 }}</span>
              <div class="stat-bar">
                <div class="stat-fill" :style="{ width: getStatPercentage(pokemon.sp_def) }"></div>
              </div>
            </div>
            <div class="stat-item">
              <span class="stat-label">速度</span>
              <span class="stat-value">{{ pokemon.speed || 0 }}</span>
              <div class="stat-bar">
                <div class="stat-fill" :style="{ width: getStatPercentage(pokemon.speed) }"></div>
              </div>
            </div>
            <div class="stat-item total">
              <span class="stat-label">总计</span>
              <span class="stat-value">{{ pokemon.total || 0 }}</span>
            </div>
          </div>
        </div>

        <div class="info-card" v-if="pokemon.description">
          <h2>宝可梦介绍</h2>
          <p class="description">{{ pokemon.description }}</p>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading">
    <p>加载中...</p>
  </div>

  <div v-else-if="error" class="error">
    <p>{{ error }}</p>
    <button @click="loadPokemon">重试</button>
  </div>
</template>

<script>
import { pokemonAPI } from '@/services/api.js'

export default {
  name: 'PokemonDetail',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      pokemon: null,
      loading: true,
      error: null
    }
  },
  computed: {
    hasStats() {
      return this.pokemon && (
        this.pokemon.hp ||
        this.pokemon.attack ||
        this.pokemon.defense ||
        this.pokemon.sp_atk ||
        this.pokemon.sp_def ||
        this.pokemon.speed
      )
    }
  },
  async mounted() {
    await this.loadPokemon()
  },
  watch: {
    id: {
      handler: 'loadPokemon',
      immediate: false
    }
  },
  methods: {
    async loadPokemon() {
      this.loading = true
      this.error = null

      try {
        this.pokemon = await pokemonAPI.getPokemonById(this.id)
      } catch (error) {
        this.error = error.message
        console.error('加载宝可梦详情失败:', error)
      } finally {
        this.loading = false
      }
    },

    goBack() {
      this.$router.go(-1)
    },

    getPokemonTypes(pokemon) {
      const types = []
      if (pokemon.type1) types.push(pokemon.type1)
      if (pokemon.type2) types.push(pokemon.type2)
      return types
    },

    getPokemonImage(pokemon) {
      return `/images/${pokemon.id}_${pokemon.name.toLowerCase()}.gif`
    },

    handleImageError(event) {
      const img = event.target
      const src = img.src
      if (src.endsWith('.gif')) {
        img.src = src.replace('.gif', '.png')
      }
    },

    getStatPercentage(value) {
      if (!value) return '0%'
      // 最大种族值通常是255，转换为百分比
      return Math.min((value / 255) * 100, 100) + '%'
    }
  }
}
</script>

<style scoped>
.pokemon-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background: #5a67d8;
}

.detail-header h1 {
  color: #333;
  margin: 0;
}

.detail-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
}

.pokemon-image-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pokemon-image {
  width: 250px;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 10px;
  border: 2px solid #e9ecef;
  margin-bottom: 1rem;
}

.pokemon-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.types {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.type-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
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

.pokemon-info-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.info-card h2 {
  color: #333;
  margin-bottom: 1rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.info-grid {
  display: grid;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-weight: bold;
  color: #666;
}

.value {
  color: #333;
}

.stats-grid {
  display: grid;
  gap: 1rem;
}

.stat-item {
  display: grid;
  grid-template-columns: 60px 50px 1fr;
  align-items: center;
  gap: 1rem;
}

.stat-item.total {
  border-top: 2px solid #e9ecef;
  padding-top: 1rem;
  margin-top: 1rem;
}

.stat-label {
  font-weight: bold;
  color: #666;
  text-align: right;
}

.stat-value {
  font-weight: bold;
  color: #333;
  text-align: center;
}

.stat-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.description {
  line-height: 1.6;
  color: #555;
  white-space: pre-line;
}

.loading, .error {
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

@media (max-width: 768px) {
  .detail-content {
    grid-template-columns: 1fr;
  }

  .pokemon-image {
    width: 200px;
    height: 200px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stat-item {
    grid-template-columns: 50px 40px 1fr;
    gap: 0.5rem;
  }
}
</style>
