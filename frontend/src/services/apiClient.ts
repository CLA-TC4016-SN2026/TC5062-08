import createClient, { type Middleware } from 'openapi-fetch'
import { API_URL } from '../config'
import { getToken } from './session'
import type { paths } from './api-types'

const authMiddleware: Middleware = {
  onRequest({ request }) {
    const token = getToken()
    if (token) request.headers.set('Authorization', `Bearer ${token}`)
    return request
  },
}

export const api = createClient<paths>({ baseUrl: API_URL })
api.use(authMiddleware)
