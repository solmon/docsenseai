import {
  ComponentFixture,
  TestBed,
  fakeAsync,
  tick,
} from '@angular/core/testing'
import { Router } from '@angular/router'
import { RouterTestingModule } from '@angular/router/testing'
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing'
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http'
import { NgbActiveModal, NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap'
import { TenantSelectorComponent } from './tenant-selector.component'
import { TenantContextService } from 'src/app/services/tenant-context.service'
import { TenantService } from 'src/app/services/tenant.service'
import { TenantInterceptor } from 'src/app/interceptors/tenant.interceptor'
import { Tenant } from 'src/app/data/tenant'
import { environment } from 'src/environments/environment'

describe('TenantSelectorComponent Integration', () => {
  let component: TenantSelectorComponent
  let fixture: ComponentFixture<TenantSelectorComponent>
  let tenantContextService: TenantContextService
  let tenantService: TenantService
  let httpTestingController: HttpTestingController
  let router: Router

  const mockTenants: Tenant[] = [
    {
      id: 1,
      name: 'Test Tenant 1',
      identifier: 'test-tenant-1',
      is_active: true,
    },
    {
      id: 2,
      name: 'Test Tenant 2',
      identifier: 'test-tenant-2',
      is_active: true,
    },
  ]

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TenantSelectorComponent, NgbModule, RouterTestingModule],
      providers: [
        NgbActiveModal,
        NgbModal,
        TenantContextService,
        TenantService,
        TenantInterceptor,
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    }).compileComponents()

    tenantContextService = TestBed.inject(TenantContextService)
    tenantService = TestBed.inject(TenantService)
    httpTestingController = TestBed.inject(HttpTestingController)
    router = TestBed.inject(Router)

    sessionStorage.clear()
  })

  afterEach(() => {
    httpTestingController.verify()
    sessionStorage.clear()
  })

  it('should complete full tenant selection flow', fakeAsync(() => {
    fixture = TestBed.createComponent(TenantSelectorComponent)
    component = fixture.componentInstance
    component.tenants = mockTenants

    // Initially no tenant selected
    expect(tenantContextService.getCurrentTenant()).toBeNull()

    // Select tenant
    component.selectTenant(mockTenants[0])
    expect(component.selectedTenant).toEqual(mockTenants[0])

    // Confirm selection
    component.confirm()
    tick()

    // Verify tenant is set in context service
    expect(tenantContextService.getCurrentTenant()).toEqual(mockTenants[0])
    expect(tenantContextService.getCurrentTenantId()).toBe(1)

    // Verify tenant is persisted in sessionStorage
    expect(sessionStorage.getItem('paperless_current_tenant_id')).toBe('1')
  }))

  it('should include X-Tenant-ID header in subsequent API requests', fakeAsync(() => {
    fixture = TestBed.createComponent(TenantSelectorComponent)
    component = fixture.componentInstance
    component.tenants = mockTenants

    // Select and confirm tenant
    component.selectTenant(mockTenants[0])
    component.confirm()
    tick()

    // Make an API request - should include X-Tenant-ID header
    tenantService.getCurrentUserTenant().subscribe()

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )

    // Verify X-Tenant-ID header is present
    expect(req.request.headers.get('X-Tenant-ID')).toBe('1')
    req.flush(mockTenants[0])
  }))

  it('should initialize tenant context on app startup', fakeAsync(() => {
    // Simulate app initialization
    tenantContextService.initializeTenantContext().subscribe((tenants) => {
      expect(tenants).toEqual([mockTenants[0]])
      expect(tenantContextService.getCurrentTenant()).toEqual(mockTenants[0])
    })

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    req.flush(mockTenants[0])
    tick()

    // Verify tenant is persisted
    expect(sessionStorage.getItem('paperless_current_tenant_id')).toBe('1')
  }))

  it('should load tenant from sessionStorage on service initialization', fakeAsync(() => {
    // Set tenant in sessionStorage
    sessionStorage.setItem('paperless_current_tenant_id', '1')

    // Create new service instance (simulates app reload)
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

    // Service should load tenant from storage
    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    req.flush(mockTenants[0])
    tick()

    expect(newService.getCurrentTenantId()).toBe(1)
  }))

  it('should handle tenant switch during session', fakeAsync(() => {
    fixture = TestBed.createComponent(TenantSelectorComponent)
    component = fixture.componentInstance
    component.tenants = mockTenants

    // Select first tenant
    component.selectTenant(mockTenants[0])
    component.confirm()
    tick()

    expect(tenantContextService.getCurrentTenantId()).toBe(1)

    // Switch to second tenant
    component.selectTenant(mockTenants[1])
    component.confirm()
    tick()

    expect(tenantContextService.getCurrentTenantId()).toBe(2)
    expect(sessionStorage.getItem('paperless_current_tenant_id')).toBe('2')
  }))
})

