import { HttpEvent, HttpRequest } from '@angular/common/http'
import { TestBed } from '@angular/core/testing'
import { of } from 'rxjs'
import { TenantInterceptor } from './tenant.interceptor'
import { TenantContextService } from '../services/tenant-context.service'
import { Tenant } from '../data/tenant'

describe('TenantInterceptor', () => {
  let interceptor: TenantInterceptor
  let tenantContextService: TenantContextService

  const mockTenant: Tenant = {
    id: 1,
    name: 'Test Tenant',
    identifier: 'test-tenant',
    is_active: true,
  }

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [TenantInterceptor, TenantContextService],
    })

    interceptor = TestBed.inject(TenantInterceptor)
    tenantContextService = TestBed.inject(TenantContextService)
  })

  it('should be created', () => {
    expect(interceptor).toBeTruthy()
  })

  it('should add X-Tenant-ID header when tenant is set', () => {
    tenantContextService.setCurrentTenant(mockTenant)

    interceptor.intercept(new HttpRequest('GET', 'https://example.com'), {
      handle: (request) => {
        const header = request.headers['lazyUpdate'][0]
        expect(header.name).toEqual('X-Tenant-ID')
        expect(header.value).toEqual('1')
        return of({} as HttpEvent<any>)
      },
    })
  })

  it('should not add X-Tenant-ID header when tenant is not set', () => {
    tenantContextService.clearTenant()

    interceptor.intercept(new HttpRequest('GET', 'https://example.com'), {
      handle: (request) => {
        // Should not have X-Tenant-ID header
        const headers = request.headers['lazyUpdate'] || []
        const tenantHeader = headers.find((h: any) => h.name === 'X-Tenant-ID')
        expect(tenantHeader).toBeUndefined()
        return of({} as HttpEvent<any>)
      },
    })
  })

  it('should update header when tenant changes', () => {
    const tenant2: Tenant = {
      id: 2,
      name: 'Another Tenant',
      identifier: 'another-tenant',
      is_active: true,
    }

    tenantContextService.setCurrentTenant(mockTenant)

    interceptor.intercept(new HttpRequest('GET', 'https://example.com'), {
      handle: (request) => {
        let header = request.headers['lazyUpdate'][0]
        expect(header.value).toEqual('1')

        // Change tenant
        tenantContextService.setCurrentTenant(tenant2)

        // Intercept again
        interceptor.intercept(new HttpRequest('GET', 'https://example.com'), {
          handle: (request2) => {
            header = request2.headers['lazyUpdate'][0]
            expect(header.value).toEqual('2')
            return of({} as HttpEvent<any>)
          },
        })

        return of({} as HttpEvent<any>)
      },
    })
  })
})

