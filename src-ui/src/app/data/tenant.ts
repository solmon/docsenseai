import { ObjectWithId } from './object-with-id'

export interface Tenant extends ObjectWithId {
  name: string
  identifier: string
  is_active: boolean
  created_at?: string
  updated_at?: string
  deleted_at?: string | null
}

