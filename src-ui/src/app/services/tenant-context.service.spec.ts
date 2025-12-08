import { TestBed } from '@angular/core/testing'
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing'
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http'
import { TenantContextService } from './tenant-context.service'
import { TenantService } from './tenant.service'
import { Tenant } from '../data/tenant'
import { environment } from 'src/environments/environment'

describe('TenantContextService', () => {
  let service: TenantContextService
  let tenantService: TenantService
  let httpTestingController: HttpTestingController

  const mockTenant: Tenant = {
    id: 1,
    name: 'Test Tenant',
    identifier: 'test-tenant',
    is_active: true,
  }

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TenantContextService,
        TenantService,
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    })

    service = TestBed.inject(TenantContextService)
    tenantService = TestBed.inject(TenantService)
    httpTestingController = TestBed.inject(HttpTestingController)

    // Clear sessionStorage before each test
    sessionStorage.clear()
  })

  afterEach(() => {
    httpTestingController.verify()
    sessionStorage.clear()
  })

  it('should be created', () => {
    expect(service).toBeTruthy()
  })

  it('should return null for current tenant initially', () => {
    expect(service.getCurrentTenant()).toBeNull()
    expect(service.getCurrentTenantId()).toBeNull()
  })

  it('should set and get current tenant', () => {
    service.setCurrentTenant(mockTenant)

    expect(service.getCurrentTenant()).toEqual(mockTenant)
    expect(service.getCurrentTenantId()).toBe(1)
  })

  it('should persist tenant in sessionStorage', () => {
    service.setCurrentTenant(mockTenant)

    expect(sessionStorage.getItem('paperless_current_tenant_id')).toBe('1')
  })

  it('should clear tenant from sessionStorage', () => {
    service.setCurrentTenant(mockTenant)
    service.clearTenant()

    expect(service.getCurrentTenant()).toBeNull()
    expect(sessionStorage.getItem('paperless_current_tenant_id')).toBeNull()
  })

  it('should emit current tenant changes', (done) => {
    service.currentTenant$.subscribe((tenant) => {
      if (tenant) {
        expect(tenant).toEqual(mockTenant)
        done()
      }
    })

    service.setCurrentTenant(mockTenant)
  })

  it('should initialize tenant context from API', () => {
    service.initializeTenantContext().subscribe((tenants) => {
      expect(tenants).toEqual([mockTenant])
      expect(service.getCurrentTenant()).toEqual(mockTenant)
    })

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    expect(req.request.method).toEqual('GET')
    req.flush(mockTenant)
  })

  it('should handle API error during initialization', () => {
    service.initializeTenantContext().subscribe((tenants) => {
      expect(tenants).toEqual([])
      expect(service.getCurrentTenant()).toBeNull()
    })

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    req.error(new ErrorEvent('Network error'), { status: 404 })
  })

  it('should load tenant from sessionStorage on initialization', () => {
    sessionStorage.setItem('paperless_current_tenant_id', '1')

    // Create new service instance to trigger constructor
    const newService = new TenantContextService()
    TestBed.resetTestingModule()
    TestBed.configureTestingModule({
      providers: [
        { provide: TenantContextService, useValue: newService },
        TenantService,
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    })

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    req.flush(mockTenant)

    // Service should have loaded tenant
    expect(newService.getCurrentTenantId()).toBe(1)
  })
})

