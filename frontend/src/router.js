import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import PokemonList from './views/PokemonList.vue'
import PokemonDetail from './views/PokemonDetail.vue'
import Stats from './views/Stats.vue'
import ItemsList from './views/ItemsList.vue'
import MovesList from './views/MovesList.vue'

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
    path: '/items',
    name: 'ItemsList',
    component: ItemsList
  },
  {
    path: '/moves',
    name: 'MovesList',
    component: MovesList
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
