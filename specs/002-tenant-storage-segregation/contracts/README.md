# API Contracts

**Feature**: Tenant-Level Storage Segregation

## No API Changes Required

This feature does not modify any API endpoints or contracts. Tenant-level storage segregation is an internal implementation detail that is transparent to API consumers.

All existing API endpoints continue to function identically:
- Document upload endpoints
- Document retrieval endpoints
- Document deletion endpoints
- Archive endpoints
- Thumbnail endpoints

The tenant segregation is handled automatically by the storage backend layer, with no changes to request/response formats, authentication, or behavior from the client perspective.

