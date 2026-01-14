# 宝可梦图鉴前端

基于 Vue 3 + Vite 的现代化宝可梦图鉴前端应用。

## 功能特性

- 🏠 **首页**: 应用介绍和数据库统计概览
- 📋 **宝可梦列表**: 支持分页、搜索和属性过滤
- 🔍 **详情页面**: 完整的宝可梦信息展示
- 📊 **统计页面**: 数据可视化和分析
- 🎨 **现代化UI**: 响应式设计，支持移动端

## 技术栈

- **Vue 3**: 组合式 API
- **Vue Router**: 单页面应用路由
- **Axios**: HTTP 客户端
- **Vite**: 快速构建工具
- **CSS Grid & Flexbox**: 现代布局

## 安装依赖

确保你已经安装了 pnpm、Node.js 和 fnm：

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install
```

## 运行开发服务器

```bash
# 启动开发服务器
pnpm dev

# 或直接使用
npm run dev
```

开发服务器将在 `http://localhost:5173` 启动。

## 构建生产版本

```bash
# 构建生产版本
pnpm build

# 预览构建结果
pnpm preview
```

## 项目结构

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   ├── Home.vue        # 首页
│   │   ├── PokemonList.vue # 宝可梦列表
│   │   ├── PokemonDetail.vue # 详情页面
│   │   └── Stats.vue       # 统计页面
│   ├── services/
│   │   └── api.js          # API 服务
│   ├── router.js           # 路由配置
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── public/               # 静态资源
├── package.json          # 项目配置
├── vite.config.js        # Vite 配置
└── README.md            # 项目说明
```

## API 集成

前端通过 Axios 与后端 FastAPI 服务器通信：

- 开发环境: 代理到 `http://localhost:8000`
- 生产环境: 需要配置相应的 API 地址

## 主要组件

### Home.vue
- 应用介绍
- 数据库统计概览
- 快速导航

### PokemonList.vue
- 宝可梦卡片网格布局
- 搜索功能 (按名称)
- 属性过滤器
- 分页加载

### PokemonDetail.vue
- 详细的宝可梦信息
- 种族值可视化图表
- 图片展示
- 返回导航

### Stats.vue
- 数据统计卡片
- 属性分布柱状图
- 种族值分析

## 样式说明

- 使用现代 CSS 特性 (Grid, Flexbox)
- 响应式设计，适配移动端
- 宝可梦属性颜色系统
- 平滑动画过渡效果

## 开发说明

1. 确保后端服务器正在运行 (`python main.py`)
2. 启动前端开发服务器 (`pnpm dev`)
3. 在浏览器中访问 `http://localhost:5173`

## 注意事项

- 前端依赖后端 API 服务
- 图片资源通过后端静态文件服务提供
- CORS 配置已启用，支持跨域请求
