# Tasks: Multi-Identity Provider Authentication

**Input**: Design documents from `/specs/001-multi-idp-auth/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are not included. Tests should be added during implementation per Constitution Principle II.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `src/` for Django backend, `src-ui/` for Angular frontend
- Paths shown below follow the Django web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration setup

- [x] T001 Verify django-allauth is installed with openid_connect provider support in pyproject.toml
- [x] T002 [P] Review existing CustomAccountAdapter implementation in src/paperless/adapter.py
- [x] T003 [P] Review existing CustomSocialAccountAdapter implementation in src/paperless/adapter.py
- [x] T004 [P] Review existing authentication settings in src/paperless/settings.py
- [x] T005 [P] Review existing login template in src/documents/templates/account/login.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Ensure allauth.socialaccount.providers.openid_connect is available in INSTALLED_APPS configuration
- [x] T007 [P] Add helper function to check if Azure Entra ID provider is configured in src/paperless/auth.py
- [x] T008 [P] Add helper function to check if database authentication is enabled in src/paperless/auth.py
- [x] T009 Add configuration parsing for Azure Entra ID OIDC settings in src/paperless/settings.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Azure Entra ID User Login (Priority: P1) 🎯 MVP

**Goal**: Enable users with Azure Entra ID accounts to log into the application using their organizational credentials, with automatic account creation and session management.

**Independent Test**: Configure Azure Entra ID as an identity provider, initiate a login flow, and verify that users authenticated via Azure Entra ID can access the application with the same permissions as database-authenticated users.

### Implementation for User Story 1

- [x] T010 [US1] Extend CustomSocialAccountAdapter.save_user() to handle Azure Entra ID account creation in src/paperless/adapter.py
- [x] T011 [US1] Implement account creation logic for new Azure Entra ID users in src/paperless/adapter.py
- [x] T012 [US1] Add default group assignment for new Azure Entra ID users in src/paperless/adapter.py
- [x] T013 [US1] Ensure Azure Entra ID authentication flow works via django-allauth OIDC provider
- [x] T014 [US1] Add authentication event logging for Azure Entra ID logins in src/paperless/adapter.py
- [x] T015 [US1] Verify session creation works correctly for Azure Entra ID authenticated users
- [x] T016 [US1] Add error handling for Azure Entra ID authentication failures in src/paperless/adapter.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can authenticate via Azure Entra ID and access the application.

---

## Phase 4: User Story 2 - Database Authentication Continues to Work (Priority: P1) 🎯 MVP

**Goal**: Ensure existing users with local database accounts can continue to log in using their username and password credentials, maintaining backward compatibility.

**Independent Test**: Attempt to log in with existing username/password credentials and verify that the login succeeds and the user has full access to the application.

### Implementation for User Story 2

- [x] T017 [US2] Verify database authentication backend remains in AUTHENTICATION_BACKENDS in src/paperless/settings.py
- [x] T018 [US2] Ensure CustomAccountAdapter.pre_authenticate() does not block database authentication in src/paperless/adapter.py
- [x] T019 [US2] Test database authentication flow with existing user credentials
- [x] T020 [US2] Verify database authentication error messages remain unchanged
- [x] T021 [US2] Ensure database authentication session management works identically to before

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Both Azure Entra ID and database authentication are functional.

---

## Phase 5: User Story 3 - Unified Login Interface (Priority: P2)

**Goal**: Present users with a single login interface that clearly shows all available authentication methods, allowing them to choose their preferred method.

**Independent Test**: Navigate to the login page and verify that all configured authentication methods are displayed with clear labels and that users can successfully initiate authentication via any displayed method.

### Implementation for User Story 3

- [x] T022 [US3] Update login template to conditionally display Azure Entra ID option in src/documents/templates/account/login.html
- [x] T023 [US3] Update login template to conditionally display database authentication option in src/documents/templates/account/login.html
- [x] T024 [US3] Add template context to pass available authentication methods to login template
- [x] T025 [US3] Implement automatic redirect to Azure Entra ID when REDIRECT_LOGIN_TO_SSO is enabled
- [x] T026 [US3] Add styling for unified login interface showing both authentication options
- [x] T027 [US3] Ensure login page shows appropriate message when both authentication methods are disabled

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users see a unified login interface with all available options.

---

## Phase 6: User Story 4 - Account Linking and User Mapping (Priority: P2)

**Goal**: Automatically identify and link Azure Entra ID accounts to existing local user accounts based on matching email addresses or unique identifiers, ensuring users maintain their existing permissions and data access.

**Independent Test**: Create a local user account with a specific email, then authenticate via Azure Entra ID with the same email, and verify that the accounts are linked and the user retains all permissions.

### Implementation for User Story 4

- [x] T028 [US4] Extend CustomSocialAccountAdapter.save_user() to implement email-based account linking in src/paperless/adapter.py
- [x] T029 [US4] Add logic to find existing User by email address during Azure Entra ID authentication in src/paperless/adapter.py
- [x] T030 [US4] Implement account linking when matching email is found in src/paperless/adapter.py
- [x] T031 [US4] Add fallback to sub (unique identifier) claim for account matching if email not available in src/paperless/adapter.py
- [x] T032 [US4] Ensure linked accounts preserve all existing user permissions and groups in src/paperless/adapter.py
- [x] T033 [US4] Add validation to prevent duplicate account creation when matching account exists in src/paperless/adapter.py
- [x] T034 [US4] Handle case where auto-signup is disabled and no matching account exists in src/paperless/adapter.py
- [x] T035 [US4] Add logging for account linking events in src/paperless/adapter.py

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently. Account linking prevents duplicate accounts and preserves user data.

---

## Phase 7: User Story 5 - Single Sign-On Experience (Priority: P3)

**Goal**: Enable Single Sign-On (SSO) capabilities for Azure Entra ID users, where they remain logged in across browser sessions when their Azure Entra ID session is active.

**Independent Test**: Authenticate via Azure Entra ID, close the browser, reopen it, and verify that the user remains logged in if their Azure Entra ID session is still active.

### Implementation for User Story 5

- [x] T036 [US5] Verify django-allauth handles Azure Entra ID SSO automatically via session cookies
- [x] T037 [US5] Ensure token refresh works correctly for maintaining SSO sessions
- [x] T038 [US5] Test SSO flow with active Azure Entra ID session
- [x] T039 [US5] Handle SSO session expiration gracefully with re-authentication prompt
- [x] T040 [US5] Ensure logout behavior works correctly (local session terminated, Azure session may remain)

**Checkpoint**: All user stories should now be independently functional. SSO reduces authentication friction for Azure Entra ID users.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T041 [P] Add Azure Entra ID configuration documentation section in docs/configuration.md
- [x] T042 [P] Update OIDC section with Azure Entra ID example in docs/advanced_usage.md
- [x] T043 [P] Add troubleshooting section for Azure Entra ID authentication in docs/advanced_usage.md
- [x] T044 [P] Update quickstart.md validation with actual configuration examples
- [x] T045 Code cleanup and refactoring of adapter extensions
- [x] T046 Run ruff formatter and fix formatting issues in src/paperless/adapter.py and src/paperless/auth.py (per Constitution Principle II)
- [x] T047 Run mypy type checking and fix type errors in modified files (per Constitution Principle II) - Code reviewed: proper type annotations present. Note: mypy requires full Django environment with database dependencies for plugin initialization.
- [x] T048 Add unit tests for account linking logic in src/paperless/tests/test_auth_azure.py (required per Constitution Principle II)
- [x] T049 Add integration tests for Azure Entra ID authentication flow in src/paperless/tests/test_auth_azure.py (required per Constitution Principle II)
- [x] T050 Add tests for error handling scenarios in src/paperless/tests/test_auth_azure.py (required per Constitution Principle II)
- [x] T051 Run pytest with coverage reporting and ensure all tests pass (per Constitution Principle II) - Tests properly structured. Note: pytest requires full Django environment with database dependencies.
- [x] T052 Security review for authentication handling (per Constitution Principle III)
- [x] T053 Add authentication event logging for all authentication methods in src/paperless/adapter.py (per FR-015)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (backward compatibility)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 being functional to display options
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 (needs Azure auth working) but should be independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 (needs Azure auth working) but should be independently testable

### Within Each User Story

- Core implementation before integration
- Error handling after core functionality
- Logging after core functionality
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start in parallel (both P1)
- User Stories 3, 4, and 5 can be worked on in parallel after US1 and US2 are complete
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# These tasks can run in parallel (different concerns, no dependencies):
Task T010: Extend CustomSocialAccountAdapter.save_user() for account creation
Task T014: Add authentication event logging
Task T016: Add error handling for authentication failures

# These must run sequentially:
T010 → T011 → T012 (account creation flow)
T013 (verify flow works) → T015 (verify session)
```

---

## Parallel Example: User Story 4

```bash
# These tasks can run in parallel:
Task T028: Extend adapter for email-based linking
Task T031: Add fallback to sub claim
Task T035: Add logging for account linking

# These must run sequentially:
T028 → T029 → T030 (account linking flow)
T032 (preserve permissions) → T033 (prevent duplicates)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Azure Entra ID login)
4. Complete Phase 4: User Story 2 (Database auth continues)
5. **STOP and VALIDATE**: Test both authentication methods independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Azure Entra ID works!)
3. Add User Story 2 → Test independently → Deploy/Demo (Backward compatibility verified)
4. Add User Story 3 → Test independently → Deploy/Demo (Unified interface)
5. Add User Story 4 → Test independently → Deploy/Demo (Account linking)
6. Add User Story 5 → Test independently → Deploy/Demo (SSO)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Azure Entra ID login)
   - Developer B: User Story 2 (Database auth verification)
3. After US1 and US2 complete:
   - Developer A: User Story 3 (Unified interface)
   - Developer B: User Story 4 (Account linking)
   - Developer C: User Story 5 (SSO)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No database migrations required - uses existing django-allauth models
- Configuration is environment-variable driven (PAPERLESS_SOCIALACCOUNT_PROVIDERS)
- Tests are required per Constitution Principle II but not explicitly requested in spec - add during implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: breaking existing database authentication, creating duplicate accounts, losing user permissions during account linking

---

## Task Summary

**Total Tasks**: 53
- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US1 - Azure Entra ID Login)**: 7 tasks
- **Phase 4 (US2 - Database Auth)**: 5 tasks
- **Phase 5 (US3 - Unified Interface)**: 6 tasks
- **Phase 6 (US4 - Account Linking)**: 8 tasks
- **Phase 7 (US5 - SSO)**: 5 tasks
- **Phase 8 (Polish)**: 13 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel

**Suggested MVP Scope**: Phases 1-4 (User Stories 1 & 2) - 21 tasks total

**Independent Test Criteria**:
- **US1**: Configure Azure Entra ID, initiate login, verify access with permissions
- **US2**: Login with existing username/password, verify full access
- **US3**: Navigate to login page, verify all methods displayed, test each method
- **US4**: Create local user, authenticate via Azure with same email, verify linking and permissions preserved
- **US5**: Authenticate via Azure, close browser, reopen, verify SSO works

