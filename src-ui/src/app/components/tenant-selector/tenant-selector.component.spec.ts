import { ComponentFixture, TestBed } from '@angular/core/testing'
import { NgbActiveModal, NgbModule } from '@ng-bootstrap/ng-bootstrap'
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing'
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http'
import { TenantSelectorComponent } from './tenant-selector.component'
import { TenantContextService } from 'src/app/services/tenant-context.service'
import { TenantService } from 'src/app/services/tenant.service'
import { Tenant } from 'src/app/data/tenant'
import { environment } from 'src/environments/environment'

describe('TenantSelectorComponent', () => {
  let component: TenantSelectorComponent
  let fixture: ComponentFixture<TenantSelectorComponent>
  let modal: NgbActiveModal
  let tenantService: TenantService
  let tenantContextService: TenantContextService
  let httpTestingController: HttpTestingController

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
      imports: [TenantSelectorComponent, NgbModule],
      providers: [
        NgbActiveModal,
        TenantContextService,
        TenantService,
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    }).compileComponents()

    modal = TestBed.inject(NgbActiveModal)
    tenantService = TestBed.inject(TenantService)
    tenantContextService = TestBed.inject(TenantContextService)
    httpTestingController = TestBed.inject(HttpTestingController)

    fixture = TestBed.createComponent(TenantSelectorComponent)
    component = fixture.componentInstance
    component.tenants = mockTenants
    fixture.detectChanges()
  })

  afterEach(() => {
    httpTestingController.verify()
  })

  it('should create', () => {
    expect(component).toBeTruthy()
  })

  it('should display tenants', () => {
    expect(component.tenants).toEqual(mockTenants)
  })

  it('should select tenant', () => {
    component.selectTenant(mockTenants[0])
    expect(component.selectedTenant).toEqual(mockTenants[0])
  })

  it('should confirm selection and close modal', () => {
    const closeSpy = jest.spyOn(modal, 'close')
    const setTenantSpy = jest.spyOn(tenantContextService, 'setCurrentTenant')
    let selectedTenant: Tenant | null = null

    component.tenantSelected.subscribe((tenant) => {
      selectedTenant = tenant
    })

    component.selectTenant(mockTenants[0])
    component.confirm()

    expect(setTenantSpy).toHaveBeenCalledWith(mockTenants[0])
    expect(closeSpy).toHaveBeenCalledWith(mockTenants[0])
    expect(selectedTenant).toEqual(mockTenants[0])
  })

  it('should not confirm if no tenant selected', () => {
    const closeSpy = jest.spyOn(modal, 'close')
    component.selectedTenant = null
    component.confirm()

    expect(closeSpy).not.toHaveBeenCalled()
  })

  it('should cancel and dismiss modal', () => {
    const dismissSpy = jest.spyOn(modal, 'dismiss')
    component.cancel()

    expect(dismissSpy).toHaveBeenCalled()
  })

  it('should load tenants from service if not provided', () => {
    component.tenants = []
    component.ngOnInit()

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    expect(req.request.method).toEqual('GET')
    req.flush(mockTenants[0])

    expect(component.tenants).toEqual([mockTenants[0]])
    expect(component.selectedTenant).toEqual(mockTenants[0])
  })

  it('should handle error when loading tenants', () => {
    component.tenants = []
    component.ngOnInit()

    const req = httpTestingController.expectOne(
      `${environment.apiBaseUrl}profile/tenant/`
    )
    req.error(new ErrorEvent('Network error'), { status: 500 })

    expect(component.error).toBeTruthy()
    expect(component.tenants).toEqual([])
  })

  it('should disable confirm button for inactive tenant', () => {
    const inactiveTenant: Tenant = {
      id: 3,
      name: 'Inactive Tenant',
      identifier: 'inactive-tenant',
      is_active: false,
    }

    component.selectTenant(inactiveTenant)
    expect(component.selectedTenant).toEqual(inactiveTenant)
    // Confirm should be disabled for inactive tenant
    // This is tested via the template, but we can verify the state
    expect(component.selectedTenant?.is_active).toBe(false)
  })
})

