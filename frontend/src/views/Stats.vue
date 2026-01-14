<template>
  <div class="stats-page">
    <h1>宝可梦数据统计</h1>

    <div v-if="loading" class="loading">
      <p>加载统计数据中...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadStats">重试</button>
    </div>

    <div v-else class="stats-content">
      <!-- 总体统计 -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-number">{{ stats.total_pokemon }}</div>
          <div class="stat-label">总宝可梦数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ Object.keys(stats.type_distribution).length }}</div>
          <div class="stat-label">属性类型数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ Math.round(stats.stats_summary.total_avg) }}</div>
          <div class="stat-label">平均种族值</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.stats_summary.total_max }}</div>
          <div class="stat-label">最高种族值</div>
        </div>
      </div>

      <!-- 属性分布 -->
      <div class="chart-section">
        <h2>属性分布</h2>
        <div class="type-chart">
          <div
            v-for="[type, count] in Object.entries(stats.type_distribution).sort((a, b) => b[1] - a[1])"
            :key="type"
            class="type-bar"
          >
            <div class="type-label">
              <span class="type-name">{{ type }}</span>
              <span class="type-count">{{ count }}</span>
            </div>
            <div class="bar-container">
              <div
                class="bar-fill"
                :class="`type-${type.toLowerCase()}`"
                :style="{ width: getBarWidth(count, Math.max(...Object.values(stats.type_distribution))) }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 种族值统计 -->
      <div class="stats-section">
        <h2>种族值统计</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-name">HP 平均值</span>
            <span class="stat-value">{{ Math.round(stats.stats_summary.hp_avg) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-name">攻击平均值</span>
            <span class="stat-value">{{ Math.round(stats.stats_summary.attack_avg) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-name">种族值范围</span>
            <span class="stat-value">{{ stats.stats_summary.total_min }} - {{ stats.stats_summary.total_max }}</span>
          </div>
        </div>
      </div>

      <!-- 数据说明 -->
      <div class="info-section">
        <h2>数据说明</h2>
        <div class="info-content">
          <p><strong>宝可梦总数：</strong>{{ stats.total_pokemon }} 只宝可梦已收录到数据库中</p>
          <p><strong>属性类型：</strong>宝可梦分为 {{ Object.keys(stats.type_distribution).length }} 种不同属性</p>
          <p><strong>种族值：</strong>反映宝可梦的基础能力，范围从 {{ stats.stats_summary.total_min }} 到 {{ stats.stats_summary.total_max }}</p>
          <p><strong>数据来源：</strong>数据来源于 Pokemon Showdown 和 52poke 百科</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { pokemonAPI } from '@/services/api.js'

export default {
  name: 'Stats',
  data() {
    return {
      stats: null,
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.loadStats()
  },
  methods: {
    async loadStats() {
      this.loading = true
      this.error = null

      try {
        this.stats = await pokemonAPI.getStats()
      } catch (error) {
        this.error = error.message
        console.error('加载统计数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    getBarWidth(count, maxCount) {
      return (count / maxCount) * 100 + '%'
    }
  }
}
</script>

<style scoped>
.stats-page {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-page h1 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #666;
  font-size: 1rem;
}

.chart-section, .stats-section, .info-section {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.chart-section h2, .stats-section h2, .info-section h2 {
  color: #333;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.type-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.type-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.type-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 120px;
  font-weight: bold;
}

.type-name {
  color: #333;
}

.type-count {
  color: #667eea;
  font-weight: bold;
}

.bar-container {
  flex: 1;
  height: 30px;
  background: #f0f0f0;
  border-radius: 15px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 15px;
  transition: width 0.5s ease;
  display: flex;
  align-items: center;
  padding-left: 10px;
  color: white;
  font-weight: bold;
  font-size: 0.9rem;
}

/* 属性颜色 */
.type-normal { background: linear-gradient(90deg, #A8A878, #B8B8A8); }
.type-fire { background: linear-gradient(90deg, #F08030, #F0A050); }
.type-water { background: linear-gradient(90deg, #6890F0, #78A0F8); }
.type-grass { background: linear-gradient(90deg, #78C850, #88D060); }
.type-electric { background: linear-gradient(90deg, #F8D030, #F8E050); }
.type-ice { background: linear-gradient(90deg, #98D8D8, #A8E8E8); }
.type-fighting { background: linear-gradient(90deg, #C03028, #D04038); }
.type-poison { background: linear-gradient(90deg, #A040A0, #B050B0); }
.type-ground { background: linear-gradient(90deg, #E0C068, #F0D078); }
.type-flying { background: linear-gradient(90deg, #A890F0, #B8A0F8); }
.type-psychic { background: linear-gradient(90deg, #F85888, #F86898); }
.type-bug { background: linear-gradient(90deg, #A8B820, #B8C830); }
.type-rock { background: linear-gradient(90deg, #B8A038, #C8B048); }
.type-ghost { background: linear-gradient(90deg, #705898, #8060A8); }
.type-dragon { background: linear-gradient(90deg, #7038F8, #8048F8); }
.type-dark { background: linear-gradient(90deg, #705848, #806058); }
.type-steel { background: linear-gradient(90deg, #B8B8D0, #C8C8E0); }
.type-fairy { background: linear-gradient(90deg, #EE99AC, #F0A9BC); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-name {
  font-weight: bold;
  color: #666;
}

.stat-value {
  font-weight: bold;
  color: #667eea;
  font-size: 1.2rem;
}

.info-content {
  line-height: 1.6;
  color: #555;
}

.info-content p {
  margin-bottom: 0.75rem;
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
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .type-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .type-label {
    min-width: auto;
    width: 100%;
  }

  .bar-container {
    width: 100%;
  }
}
</style>
