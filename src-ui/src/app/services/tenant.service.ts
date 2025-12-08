import { HttpClient } from '@angular/common/http'
import { Injectable, inject } from '@angular/core'
import { Observable } from 'rxjs'
import { environment } from 'src/environments/environment'
import { Tenant } from '../data/tenant'

@Injectable({
  providedIn: 'root',
})
export class TenantService {
  private http = inject(HttpClient)

  private endpoint = 'tenants'

  /**
   * Get current user's tenant
   */
  getCurrentUserTenant(): Observable<Tenant> {
    return this.http.get<Tenant>(`${environment.apiBaseUrl}profile/tenant/`)
  }

  /**
   * Get tenants associated with a user
   */
  getUserTenants(userId: number): Observable<Tenant[]> {
    return this.http.get<Tenant[]>(
      `${environment.apiBaseUrl}users/${userId}/tenants/`
    )
  }

  /**
   * List all tenants (super admin only) with pagination
   */
  list(
    page?: number,
    pageSize?: number,
    search?: string,
    isActive?: boolean
  ): Observable<{
    count: number
    next: string | null
    previous: string | null
    results: Tenant[]
  }> {
    let params: { [key: string]: string } = {}
    if (page) params['page'] = page.toString()
    if (pageSize) params['page_size'] = pageSize.toString()
    if (search) params['search'] = search
    if (isActive !== undefined) params['is_active'] = isActive.toString()

    const queryString = new URLSearchParams(params).toString()
    const url = `${environment.apiBaseUrl}${this.endpoint}/${queryString ? '?' + queryString : ''}`
    return this.http.get<{
      count: number
      next: string | null
      previous: string | null
      results: Tenant[]
    }>(url)
  }

  /**
   * Get tenant by ID (super admin only)
   */
  get(id: number): Observable<Tenant> {
    return this.http.get<Tenant>(
      `${environment.apiBaseUrl}${this.endpoint}/${id}/`
    )
  }

  /**
   * Create tenant (super admin only)
   */
  create(tenant: Partial<Tenant>): Observable<Tenant> {
    return this.http.post<Tenant>(
      `${environment.apiBaseUrl}${this.endpoint}/`,
      tenant
    )
  }

  /**
   * Update tenant (super admin only)
   */
  update(id: number, tenant: Partial<Tenant>): Observable<Tenant> {
    return this.http.patch<Tenant>(
      `${environment.apiBaseUrl}${this.endpoint}/${id}/`,
      tenant
    )
  }

  /**
   * Delete tenant (soft delete, super admin only)
   */
  delete(id: number): Observable<void> {
    return this.http.delete<void>(
      `${environment.apiBaseUrl}${this.endpoint}/${id}/`
    )
  }

  /**
   * Activate tenant (super admin only)
   */
  activate(id: number): Observable<Tenant> {
    return this.http.post<Tenant>(
      `${environment.apiBaseUrl}${this.endpoint}/${id}/activate/`,
      {}
    )
  }

  /**
   * Deactivate tenant (super admin only)
   */
  deactivate(id: number): Observable<Tenant> {
    return this.http.post<Tenant>(
      `${environment.apiBaseUrl}${this.endpoint}/${id}/deactivate/`,
      {}
    )
  }
}

