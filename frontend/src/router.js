import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import PokemonList from './views/PokemonList.vue'
import PokemonDetail from './views/PokemonDetail.vue'
import Stats from './views/Stats.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/pokemon',
    name: 'PokemonList',
    component: PokemonList
  },
  {
    path: '/pokemon/:id',
    name: 'PokemonDetail',
    component: PokemonDetail,
    props: true
  },
  {
    path: '/stats',
    name: 'Stats',
    component: Stats
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
