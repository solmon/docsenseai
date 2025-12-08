import { inject } from '@angular/core'
import { Router, CanActivateFn } from '@angular/router'
import { SettingsService } from '../services/settings.service'

export const superAdminGuard: CanActivateFn = () => {
  const settingsService = inject(SettingsService)
  const router = inject(Router)

  if (settingsService.currentUser?.is_superuser) {
    return true
  }

  // Redirect to home if not super admin
  router.navigate(['/'])
  return false
}

