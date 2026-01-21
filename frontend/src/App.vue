<template>
  <div id="app">
    <header class="header">
      <h1>宝可梦图鉴</h1>
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/pokemon">宝可梦列表</router-link>
        <router-link to="/items">物品列表</router-link>
        <router-link to="/moves">技能列表</router-link>
        <router-link to="/stats">统计信息</router-link>
      </nav>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>&copy; 2024 宝可梦图鉴. 基于 Vue 3 & FastAPI</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header h1 {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 2.5rem;
}

.header nav {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.header nav a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.header nav a:hover,
.header nav a.router-link-active {
  background-color: rgba(255,255,255,0.2);
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  background-color: #333;
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}

@media (max-width: 768px) {
  .header nav {
    flex-direction: column;
    gap: 1rem;
  }

  .main-content {
    padding: 1rem;
  }
}
</style>
