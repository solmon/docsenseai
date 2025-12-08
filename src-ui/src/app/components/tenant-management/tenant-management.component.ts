import { Component, inject, OnDestroy, OnInit } from '@angular/core'
import { DatePipe } from '@angular/common'
import { FormsModule } from '@angular/forms'
import { NgbModal, NgbPaginationModule } from '@ng-bootstrap/ng-bootstrap'
import { NgxBootstrapIconsModule } from 'ngx-bootstrap-icons'
import { takeUntil } from 'rxjs'
import { Tenant } from 'src/app/data/tenant'
import { LoadingComponentWithPermissions } from '../loading-component/loading.component'
import { ConfirmDialogComponent } from '../common/confirm-dialog/confirm-dialog.component'
import { PageHeaderComponent } from '../common/page-header/page-header.component'
import { TenantEditDialogComponent } from './tenant-edit-dialog.component'
import { TenantService } from 'src/app/services/tenant.service'
import { ToastService } from 'src/app/services/toast.service'

@Component({
  selector: 'pngx-tenant-management',
  templateUrl: './tenant-management.component.html',
  styleUrls: ['./tenant-management.component.scss'],
  standalone: true,
  imports: [
    FormsModule,
    NgbPaginationModule,
    NgxBootstrapIconsModule,
    PageHeaderComponent,
    DatePipe,
  ],
})
export class TenantManagementComponent
  extends LoadingComponentWithPermissions
  implements OnInit, OnDestroy
{
  private tenantService = inject(TenantService)
  private modalService = inject(NgbModal)
  private toastService = inject(ToastService)

  tenants: Tenant[] = []
  page = 1
  pageSize = 25
  collectionSize = 0
  searchFilter = ''
  statusFilter: boolean | null = null
  show = false

  ngOnInit(): void {
    this.reloadData()
  }

  ngOnDestroy(): void {
    super.ngOnDestroy()
  }

  reloadData(): void {
    this.loading = true
    this.tenantService
      .list(
        this.page,
        this.pageSize,
        this.searchFilter || undefined,
        this.statusFilter !== null ? this.statusFilter : undefined
      )
      .pipe(takeUntil(this.unsubscribeNotifier))
      .subscribe({
        next: (response) => {
          this.tenants = response.results
          this.collectionSize = response.count
          this.loading = false
          this.show = true
        },
        error: (error) => {
          this.toastService.showError($localize`Error loading tenants`)
          this.loading = false
        },
      })
  }

  openCreateDialog(): void {
    const modal = this.modalService.open(TenantEditDialogComponent, {
      backdrop: 'static',
    })
    modal.componentInstance.dialogMode = 'create'
    modal.componentInstance.succeeded
      .pipe(takeUntil(this.unsubscribeNotifier))
      .subscribe(() => {
        this.reloadData()
      })
  }

  openEditDialog(tenant: Tenant): void {
    const modal = this.modalService.open(TenantEditDialogComponent, {
      backdrop: 'static',
    })
    modal.componentInstance.dialogMode = 'edit'
    modal.componentInstance.object = tenant
    modal.componentInstance.succeeded
      .pipe(takeUntil(this.unsubscribeNotifier))
      .subscribe(() => {
        this.reloadData()
      })
  }

  activateTenant(tenant: Tenant): void {
    this.tenantService
      .activate(tenant.id)
      .pipe(takeUntil(this.unsubscribeNotifier))
      .subscribe({
        next: () => {
          this.toastService.showInfo($localize`Tenant activated`)
          this.reloadData()
        },
        error: () => {
          this.toastService.showError($localize`Error activating tenant`)
        },
      })
  }

  deactivateTenant(tenant: Tenant): void {
    const modal = this.modalService.open(ConfirmDialogComponent, {
      backdrop: 'static',
    })
    modal.componentInstance.title = $localize`Deactivate Tenant`
    modal.componentInstance.messageBold = $localize`Do you really want to deactivate "${tenant.name}"?`
    modal.componentInstance.message = $localize`Users in this tenant will be logged out.`
    modal.componentInstance.btnClass = 'btn-warning'
    modal.componentInstance.btnCaption = $localize`Deactivate`
    modal.componentInstance.confirmClicked
      .pipe(takeUntil(this.unsubscribeNotifier))
      .subscribe(() => {
        this.tenantService
          .deactivate(tenant.id)
          .pipe(takeUntil(this.unsubscribeNotifier))
          .subscribe({
            next: () => {
              this.toastService.showInfo($localize`Tenant deactivated`)
              this.reloadData()
            },
            error: () => {
              this.toastService.showError($localize`Error deactivating tenant`)
            },
          })
        modal.close()
      })
  }

  deleteTenant(tenant: Tenant): void {
    const modal = this.modalService.open(ConfirmDialogComponent, {
      backdrop: 'static',
    })
    modal.componentInstance.title = $localize`Delete Tenant`
    modal.componentInstance.messageBold = $localize`Do you really want to delete "${tenant.name}"?`
    modal.componentInstance.message = $localize`This will soft delete the tenant. This operation cannot be undone.`
    modal.componentInstance.btnClass = 'btn-danger'
    modal.componentInstance.btnCaption = $localize`Delete`
    modal.componentInstance.confirmClicked
      .pipe(takeUntil(this.unsubscribeNotifier))
      .subscribe(() => {
        this.tenantService
          .delete(tenant.id)
          .pipe(takeUntil(this.unsubscribeNotifier))
          .subscribe({
            next: () => {
              this.toastService.showInfo($localize`Tenant deleted`)
              this.reloadData()
            },
            error: () => {
              this.toastService.showError($localize`Error deleting tenant`)
            },
          })
        modal.close()
      })
  }

  onSearchChange(): void {
    this.page = 1
    this.reloadData()
  }

  onStatusFilterChange(): void {
    this.page = 1
    this.reloadData()
  }
}

