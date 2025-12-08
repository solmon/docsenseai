import { Component, EventEmitter, inject, Input, OnDestroy, OnInit, Output } from '@angular/core'
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms'
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap'
import { takeUntil } from 'rxjs'
import { Tenant } from 'src/app/data/tenant'
import { LoadingComponentWithPermissions } from '../loading-component/loading.component'
import { TextComponent } from '../common/input/text/text.component'
import { CheckComponent } from '../common/input/check/check.component'
import { TenantService } from 'src/app/services/tenant.service'
import { ToastService } from 'src/app/services/toast.service'

@Component({
  selector: 'pngx-tenant-edit-dialog',
  templateUrl: './tenant-edit-dialog.component.html',
  styleUrls: ['./tenant-edit-dialog.component.scss'],
  standalone: true,
  imports: [ReactiveFormsModule, TextComponent, CheckComponent],
})
export class TenantEditDialogComponent
  extends LoadingComponentWithPermissions
  implements OnInit, OnDestroy
{
  activeModal = inject(NgbActiveModal)
  private tenantService = inject(TenantService)
  private toastService = inject(ToastService)

  @Input()
  dialogMode: 'create' | 'edit' = 'create'

  @Input()
  object: Tenant

  @Output()
  succeeded = new EventEmitter<Tenant>()

  @Output()
  failed = new EventEmitter()

  networkActive = false
  closeEnabled = false
  error: any = null

  objectForm: FormGroup

  ngOnInit(): void {
    this.objectForm = new FormGroup({
      name: new FormControl('', [Validators.required]),
      identifier: new FormControl('', [
        Validators.required,
        Validators.pattern(/^[a-z0-9-]+$/),
      ]),
      is_active: new FormControl(true),
    })

    if (this.object && this.dialogMode === 'edit') {
      this.objectForm.patchValue(this.object)
    }
  }

  ngOnDestroy(): void {
    super.ngOnDestroy()
  }

  getTitle(): string {
    return this.dialogMode === 'create'
      ? $localize`Create Tenant`
      : $localize`Edit Tenant`
  }

  cancel(): void {
    this.activeModal.dismiss()
  }

  save(): void {
    if (this.objectForm.invalid) {
      this.objectForm.markAllAsTouched()
      return
    }

    this.networkActive = true
    this.closeEnabled = false
    this.error = null

    const formValue = this.objectForm.value

    const operation =
      this.dialogMode === 'create'
        ? this.tenantService.create(formValue)
        : this.tenantService.update(this.object.id, formValue)

    operation.pipe(takeUntil(this.unsubscribeNotifier)).subscribe({
      next: (tenant) => {
        this.networkActive = false
        this.closeEnabled = true
        this.toastService.showInfo(
          this.dialogMode === 'create'
            ? $localize`Tenant created`
            : $localize`Tenant updated`
        )
        this.succeeded.emit(tenant)
        this.activeModal.close(tenant)
      },
      error: (error) => {
        this.networkActive = false
        this.closeEnabled = true
        this.error = error.error || { detail: 'An error occurred' }
        this.toastService.showError(
          this.dialogMode === 'create'
            ? $localize`Error creating tenant`
            : $localize`Error updating tenant`
        )
      },
    })
  }
}

