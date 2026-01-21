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
            <div class="info-item" v-if="pokemon.height">
              <span class="label">身高:</span>
              <span class="value">{{ pokemon.height }} m</span>
            </div>
            <div class="info-item" v-if="pokemon.weight">
              <span class="label">体重:</span>
              <span class="value">{{ pokemon.weight }} kg</span>
            </div>
            <div class="info-item" v-if="genderRatioText">
              <span class="label">雌雄比例:</span>
              <span class="value">{{ genderRatioText }}</span>
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

        <!-- 进化链 -->
        <div class="info-card" v-if="evolutionChain && evolutionChain.length > 0">
          <h2>进化链</h2>
          <div class="evolution-chain">
            <div
              v-for="(stage, index) in evolutionChain"
              :key="stage.name"
              class="evolution-item"
            >
              <div class="evolution-arrow" v-if="index > 0">
                <div class="arrow-line">→</div>
                <div class="evolution-condition" v-if="stage.condition">
                  {{ stage.condition }}
                </div>
              </div>
              <div class="evolution-pokemon">
                <div class="evolution-image">
                  <img
                    :src="`/images/${stage.id}_${stage.name.toLowerCase()}.gif`"
                    :alt="stage.name"
                    @error="handleEvolutionImageError"
                  >
                </div>
                <div class="evolution-name">{{ stage.name }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 可以学习的技能 -->
        <div class="info-card" v-if="moves && moves.length > 0">
          <h2>可以学习的技能</h2>
          <div class="moves-list">
            <div
              v-for="move in moves.slice(0, showAllMoves ? moves.length : 10)"
              :key="move.id"
              class="move-item"
            >
              <div class="move-info">
                <span class="move-name">{{ move.name }}</span>
                <div class="move-details">
                  <span v-if="move.type" class="move-type" :class="`type-${move.type.toLowerCase()}`">
                    {{ move.type }}
                  </span>
                  <span v-if="move.category" class="move-category">
                    {{ move.category }}
                  </span>
                  <span v-if="move.power" class="move-power">威力: {{ move.power }}</span>
                  <span v-if="move.accuracy" class="move-accuracy">命中: {{ move.accuracy }}%</span>
                  <span v-if="move.pp" class="move-pp">PP: {{ move.pp }}</span>
                  <span v-if="move.level_learned" class="move-level">Lv.{{ move.level_learned }}</span>
                </div>
              </div>
            </div>
            <button
              v-if="moves.length > 10"
              @click="showAllMoves = !showAllMoves"
              class="show-more-btn"
            >
              {{ showAllMoves ? '收起' : `显示更多 (${moves.length - 10} 个技能)` }}
            </button>
          </div>
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
      evolutions: [],
      moves: [],
      showAllMoves: false,
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
    },
    evolutionChain() {
      if (!this.pokemon || !this.evolutions || this.evolutions.length === 0) {
        return []
      }

      // API直接返回完整的进化链，按顺序排列
      return this.evolutions.map((evolution, index) => ({
        id: evolution.id,
        name: evolution.name,
        condition: evolution.condition
      }))
    },
    genderRatioText() {
      if (!this.pokemon || !this.pokemon.gender_ratio) {
        return null
      }

      try {
        // 如果gender_ratio是字符串，尝试解析为JSON
        let genderData = this.pokemon.gender_ratio
        if (typeof genderData === 'string') {
          genderData = JSON.parse(genderData)
        }

        if (typeof genderData === 'object' && genderData !== null) {
          const maleRatio = genderData.M || genderData.male || 0
          const femaleRatio = genderData.F || genderData.female || 0

          if (maleRatio === 0 && femaleRatio === 0) {
            return '无性别'
          } else if (maleRatio === 0) {
            return '仅雌性'
          } else if (femaleRatio === 0) {
            return '仅雄性'
          } else {
            const malePercent = Math.round(maleRatio * 100)
            const femalePercent = Math.round(femaleRatio * 100)
            return `雄性:${malePercent}% 雌性:${femalePercent}%`
          }
        }
      } catch (error) {
        console.error('解析雌雄比例失败:', error)
      }

      return null
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
        // 并行加载宝可梦详情、进化信息和技能信息
        const [pokemon, evolutions, moves] = await Promise.all([
          pokemonAPI.getPokemonById(this.id),
          pokemonAPI.getPokemonEvolutions(this.id).catch(() => ({ evolutions: [] })),
          this.loadPokemonMoves(this.id)
        ])

        this.pokemon = pokemon
        this.evolutions = evolutions.evolutions || []
        this.moves = moves || []
      } catch (error) {
        this.error = error.message
        console.error('加载宝可梦详情失败:', error)
      } finally {
        this.loading = false
      }
    },

    async loadPokemonMoves(pokemonId) {
      try {
        // 由于数据库中没有宝可梦-技能关联表，我们暂时返回空数组
        // 或者可以从moves表中获取所有技能作为示例
        return []
      } catch (error) {
        console.error('加载宝可梦技能失败:', error)
        return []
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

    handleEvolutionImageError(event) {
      const img = event.target
      const src = img.src
      if (src.endsWith('.gif')) {
        img.src = src.replace('.gif', '.png')
      }
    },

    getEvolutionId(name) {
      // 简化版本：假设进化后的宝可梦ID与当前宝可梦ID相同
      // 在实际应用中，需要根据名称查找对应的ID
      return this.pokemon.id
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

/* 进化链样式 */
.evolution-chain {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: center;
}

.evolution-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.evolution-arrow {
  font-size: 1.5rem;
  color: #666;
  font-weight: bold;
}

.evolution-pokemon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 100px;
}

.evolution-image {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.evolution-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.evolution-name {
  font-size: 0.9rem;
  font-weight: bold;
  color: #333;
  text-align: center;
}

.evolution-condition {
  font-size: 0.8rem;
  color: #666;
  text-align: center;
  font-style: italic;
}

/* 技能列表样式 */
.moves-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.move-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.move-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.move-name {
  font-weight: bold;
  color: #333;
  font-size: 1rem;
}

.move-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.move-type {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  text-transform: uppercase;
}

.move-category {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: #6c757d;
  color: white;
  font-size: 0.8rem;
  font-weight: bold;
}

.move-power,
.move-accuracy,
.move-pp,
.move-level {
  font-size: 0.8rem;
  color: #666;
  background: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.show-more-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
  align-self: center;
}

.show-more-btn:hover {
  background: #5a67d8;
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
