<template>
  <div class="home">
    <div class="hero">
      <h2>欢迎来到宝可梦图鉴</h2>
      <p>探索神奇的宝可梦世界，发现各种宝可梦的详细信息</p>
      <router-link to="/pokemon" class="btn-primary">开始探索</router-link>
    </div>

    <div class="features">
      <div class="feature-card">
        <h3>📚 详细资料</h3>
        <p>包含宝可梦的属性、种族值、描述等完整信息</p>
      </div>
      <div class="feature-card">
        <h3>🔍 智能搜索</h3>
        <p>支持按名称搜索，快速找到你想要的宝可梦</p>
      </div>
      <div class="feature-card">
        <h3>📊 数据统计</h3>
        <p>查看属性分布和各种统计数据</p>
      </div>
      <div class="feature-card">
        <h3>🎨 精美界面</h3>
        <p>现代化UI设计，提供优质的用户体验</p>
      </div>
    </div>

    <div class="stats-preview" v-if="!loading && stats">
      <h3>数据库统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_pokemon }}</span>
          <span class="stat-label">总宝可梦数</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ Object.keys(stats.type_distribution).length }}</span>
          <span class="stat-label">属性类型数</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ Math.round(stats.stats_summary.total_avg) }}</span>
          <span class="stat-label">平均种族值</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { pokemonAPI } from '@/services/api.js'

export default {
  name: 'Home',
  data() {
    return {
      stats: null,
      loading: true
    }
  },
  async mounted() {
    try {
      this.stats = await pokemonAPI.getStats()
    } catch (error) {
      console.error('获取统计信息失败:', error)
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
.home {
  text-align: center;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 2rem;
  border-radius: 10px;
  margin-bottom: 3rem;
}

.hero h2 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn-primary {
  display: inline-block;
  background-color: #ff6b6b;
  color: white;
  padding: 1rem 2rem;
  text-decoration: none;
  border-radius: 5px;
  font-size: 1.1rem;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #ff5252;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

.stats-preview {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.stats-preview h3 {
  margin-bottom: 2rem;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .hero h2 {
    font-size: 2rem;
  }

  .features {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
