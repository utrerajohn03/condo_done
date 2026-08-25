# Authentication and RBAC Model — Condominium Management Module

## No Separate Login System

This module does **not** build its own login, logout, password, or module-account pages. The
ARGO platform handles authentication centrally; this module only consumes the resulting JWT.

## Consuming the Platform JWT

Every protected endpoint calls `authenticate()` first, which:

1. Reads the `Authorization: Bearer <token>` header
2. Verifies the token's signature and expiry
3. Decodes the payload

## Identifying the User and Organization

The decoded payload's `sub` (user id) and `org` (organization id) become the **only** source of
identity and tenant context for the rest of the request. Nothing else in the request — body,
query string, headers, or frontend state — is ever read for this purpose.

## Preventing Organization-Context Tampering

Because `organization_id` is pulled exclusively from the verified token, a client cannot change
which organization they act as by editing the request. Even if a client sends a different
`organization_id` in the POST body, it is silently ignored (see `API_CONTRACT.md`,
`POST /api/condo/maintenance-requests`). This is enforced the same way for every write endpoint
in this module.

## Enforcing Permissions / Least Privilege

`require_permission(auth, permission)` checks the caller's role against a single
role → permission map **before any database write happens**.

Residents additionally get an **ownership check** — holding `maintenance.view` or
`maintenance.create` does not by itself let a Resident see or create requests for a unit they
are not linked to via `condo_unit_residents`. Permission and ownership are two separate checks;
both must pass.

## Role-and-Permission Matrix

| Role | View Requests | Create Request | Assign | Update Status | Delete |
|---|---|---|---|---|---|
| Resident | Own unit only | Yes (own unit) | No | Cancel own only, before Completed | No |
| Staff | Yes (all), + create on behalf of a resident | Yes | Yes | Yes | No |
| Manager | Yes (all) | Yes | Yes | Yes | Yes |
| Administrator | Yes (all) | Yes | Yes | Yes | Yes |

## Unit Records Permission Matrix

| Role | View Units | Create/Edit Units |
|---|---|---|
| Resident | Own unit only (`GET /units` and `GET /units/mine` both scoped) | No |
| Staff | Yes (all) | No |
| Manager | Yes (all) | Yes |
| Administrator | Yes (all) | Yes |

## Manage Users Permission Matrix

Local sandbox stand-in only — see `docs/ASSUMPTIONS_AND_TRADEOFFS.md`. In real ARGO, account
management is platform-owned, not a condo_ module responsibility.

| Role | View Own Profile | View Users/Residents | Add/Edit/Delete Users | Activate/Deactivate |
|---|---|---|---|---|
| Resident | Yes (own only) | No | No | No |
| Staff | Yes (own only) | Yes | No | No |
| Manager | Yes (own only) | Yes | No | No |
| Administrator | Yes (own only) | Yes | Yes | Yes |

**Design note on Manager vs. Administrator:** the panel's spec describes Manager as able to
"manage residents and users within their permitted management scope," while Administrator gets
an explicit, unambiguous list (add/edit/delete/activate/deactivate). This module interprets
Manager's scope as *managing resident-to-unit assignments* (`assignment.manage` — who is linked
to which unit) rather than raw account CRUD (`user.manage`, e.g. changing a role or deleting an
account), since assignments are data this module actually owns, while accounts are not (per the
Onboarding Contract, "FK to users — never"). If the panel intended Manager to also hold full
`user.manage`, that is a one-line change in `app/core/permissions.py`.

## Resident Assignments Permission Matrix

| Role | View Assignments | Manage Assignments (assign/end) |
|---|---|---|
| Resident | No | No |
| Staff | Yes | No |
| Manager | Yes | Yes |
| Administrator | Yes | Yes |

## Permission Names

- `maintenance.view`
- `maintenance.create`
- `maintenance.assign`
- `maintenance.update_status`
- `maintenance.delete`
- `unit.view`
- `unit.manage`
- `user.view` — view residents/users in the caller's org
- `user.manage` — add/edit/delete/activate/deactivate user accounts (Administrator only)
- `assignment.view` — view resident-to-unit assignments
- `assignment.manage` — create/end resident-to-unit assignments

Permission names are action-based (`resource.verb`), matching the platform convention, so they
compose predictably as the module grows (e.g. a future `dues.waive` permission slots in the
same way).

## Least-Privilege Design Notes

- Every write endpoint requires an explicit permission — there is no "if logged in, allow"
  fallback anywhere in this module.
- The Resident role never receives `maintenance.assign`, `maintenance.delete`, `user.view`,
  `assignment.view`, or `unit.manage` — those permissions simply do not exist in the Resident's
  role mapping, so there is no code path that could accidentally grant them.
- Ownership scoping (Resident → own unit only) is layered **on top of** the permission check,
  not instead of it — a Resident holding `maintenance.update_status` can still only apply it to
  their own request, and only to transition it to `cancelled`, and only while it has not yet
  reached `completed` (see `WORKFLOW.md`). The same pattern applies to `GET /api/condo/units`
  and `GET /api/condo/units/mine` — both are scoped to the Resident's own linked unit(s) only.
- A deactivated account (`is_active = false`) is blocked both at login (`POST /api/auth/login`)
  and on every subsequent request using an already-issued token (`get_current_auth` re-checks
  `is_active` on every call) — deactivating someone mid-session revokes access immediately
  rather than waiting for their token to expire.
