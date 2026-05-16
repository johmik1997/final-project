import { useToast } from './store/toast'
import toast from './toast'

function addToast(toast) {
  const { addToast: AT } = useToast()
  AT(toast)
}

function removeToast(id) {
  const { removeToast: RT } = useToast()
  RT(id)
}

export default toast
export {
  addToast,
  removeToast,
}