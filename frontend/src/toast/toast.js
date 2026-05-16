import Toasts from './Toasts.vue'
import { createVNode, render } from 'vue'
export default {
  install: (app) => {
    const container = document.createElement("div")
    document.body.appendChild(container)

    const vnode = createVNode(Toasts)
    vnode.appContext = app._context
    render(vnode, container)  
  }
}