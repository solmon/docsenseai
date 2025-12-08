import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http'
import { Injectable, inject } from '@angular/core'
import { Observable } from 'rxjs'
import { TenantContextService } from '../services/tenant-context.service'

@Injectable()
export class TenantInterceptor implements HttpInterceptor {
  private tenantContextService = inject(TenantContextService)

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    const tenantId = this.tenantContextService.getCurrentTenantId()

    // Add X-Tenant-ID header if tenant is set
    if (tenantId !== null) {
      request = request.clone({
        setHeaders: {
          'X-Tenant-ID': tenantId.toString(),
        },
      })
    }

    return next.handle(request)
  }
}

