import { Injectable, inject } from '@angular/core'
import { BehaviorSubject, Observable } from 'rxjs'
import { Tenant } from '../data/tenant'
import { TenantService } from './tenant.service'

@Injectable({
  providedIn: 'root',
})
export class TenantContextService {
  private tenantService = inject(TenantService)

  private currentTenantSubject = new BehaviorSubject<Tenant | null>(null)
  public currentTenant$: Observable<Tenant | null> =
    this.currentTenantSubject.asObservable()

  private readonly STORAGE_KEY = 'paperless_current_tenant_id'

  constructor() {
    // Load tenant from session storage on initialization
    this.loadTenantFromStorage()
  }

  /**
   * Get current tenant synchronously
   */
  getCurrentTenant(): Tenant | null {
    return this.currentTenantSubject.value
  }

  /**
   * Get current tenant ID
   */
  getCurrentTenantId(): number | null {
    const tenant = this.currentTenantSubject.value
    return tenant?.id ?? null
  }

  /**
   * Set current tenant
   */
  setCurrentTenant(tenant: Tenant | null): void {
    this.currentTenantSubject.next(tenant)
    if (tenant) {
      sessionStorage.setItem(this.STORAGE_KEY, tenant.id.toString())
    } else {
      sessionStorage.removeItem(this.STORAGE_KEY)
    }
  }

  /**
   * Load tenant from session storage
   */
  private loadTenantFromStorage(): void {
    const tenantIdStr = sessionStorage.getItem(this.STORAGE_KEY)
    if (tenantIdStr) {
      const tenantId = parseInt(tenantIdStr, 10)
      if (!isNaN(tenantId)) {
        // Load tenant details from API
        this.tenantService.getCurrentUserTenant().subscribe({
          next: (tenant) => {
            if (tenant.id === tenantId) {
              this.setCurrentTenant(tenant)
            } else {
              // Tenant ID mismatch, clear storage
              sessionStorage.removeItem(this.STORAGE_KEY)
            }
          },
          error: () => {
            // Failed to load tenant, clear storage
            sessionStorage.removeItem(this.STORAGE_KEY)
          },
        })
      }
    }
  }

  /**
   * Initialize tenant context for current user
   * If user has only one tenant, automatically set it
   * If user has multiple tenants, return them for selection
   */
  initializeTenantContext(): Observable<Tenant[]> {
    return new Observable((observer) => {
      this.tenantService.getCurrentUserTenant().subscribe({
        next: (tenant) => {
          // User has a tenant, set it as current
          this.setCurrentTenant(tenant)
          observer.next([tenant])
          observer.complete()
        },
        error: (error) => {
          // No tenant or error - return empty array
          observer.next([])
          observer.complete()
        },
      })
    })
  }

  /**
   * Clear current tenant
   */
  clearTenant(): void {
    this.setCurrentTenant(null)
  }
}

