import { NgFor, NgIf } from '@angular/common'
import { Component, EventEmitter, Input, OnInit, Output, inject } from '@angular/core'
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap'
import { Tenant } from 'src/app/data/tenant'
import { TenantContextService } from 'src/app/services/tenant-context.service'
import { TenantService } from 'src/app/services/tenant.service'
import { LoadingComponentWithPermissions } from '../loading-component/loading.component'

@Component({
  selector: 'pngx-tenant-selector',
  templateUrl: './tenant-selector.component.html',
  styleUrls: ['./tenant-selector.component.scss'],
  imports: [NgIf, NgFor],
})
export class TenantSelectorComponent
  extends LoadingComponentWithPermissions
  implements OnInit
{
  activeModal = inject(NgbActiveModal)
  private tenantService = inject(TenantService)
  private tenantContextService = inject(TenantContextService)

  @Input()
  tenants: Tenant[] = []

  @Input()
  title = $localize`Select Tenant`

  @Input()
  message = $localize`Please select a tenant to continue.`

  @Output()
  tenantSelected = new EventEmitter<Tenant>()

  selectedTenant: Tenant | null = null
  error: string | null = null

  // Localized strings for template
  readonly loadingTenantsText = $localize`Loading tenants...`
  readonly selectedText = $localize`Selected`
  readonly inactiveText = $localize`Inactive`
  readonly cancelText = $localize`Cancel`
  readonly selectText = $localize`Select`

  ngOnInit(): void {
    // If no tenants provided, try to load from service
    if (this.tenants.length === 0) {
      this.loadTenants()
    }
  }

  loadTenants(): void {
    this.tenantService.getCurrentUserTenant().subscribe({
      next: (tenant) => {
        this.tenants = [tenant]
        this.selectedTenant = tenant
      },
      error: (err) => {
        this.error = $localize`Failed to load tenants. Please try again.`
        console.error('Failed to load tenants:', err)
      },
    })
  }

  selectTenant(tenant: Tenant): void {
    this.selectedTenant = tenant
  }

  confirm(): void {
    if (this.selectedTenant) {
      this.tenantContextService.setCurrentTenant(this.selectedTenant)
      this.tenantSelected.emit(this.selectedTenant)
      this.activeModal.close(this.selectedTenant)
    }
  }

  cancel(): void {
    this.activeModal.dismiss()
  }
}

