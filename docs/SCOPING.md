# Scoping Brief — Condominium Management Module

**Intern:** Utrera · **Assigned prefix:** `condo_` · **Platform:** ARGO (multi-tenant SaaS)

## The Problem This Module Solves

Condominium corporations operating on the multi-tenant ARGO platform currently track units,
residents, dues, maintenance tickets, and shared-amenity bookings across spreadsheets, paper
logs, and group chats. This causes missed dues follow-up, lost maintenance tickets,
double-booked amenities, and no audit trail for who approved what.

This module gives condo staff a system to manage the core **unit** and **maintenance-request**
lifecycle inside ARGO's multi-tenant platform.

## Intended Users

| Role | What they can do |
|---|---|
| Resident / Unit Owner | View own unit, submit maintenance requests, cancel own requests |
| Front Desk Staff | View all requests, create requests, assign requests, update status |
| Property Manager | Everything Staff can do, plus delete requests |
| Administrator | Full access to all module actions |

Roles, permissions, and the authenticated user's identity all come from the **ARGO platform
JWT** — this module does not define or store its own user accounts (see
`ASSUMPTIONS_AND_TRADEOFFS.md` and `RBAC_MATRIX.md`).

## Features Included (V1)

- **Unit records** (unit number, building, floor, status), scoped per organization
- **Unit-resident linkage** (owner / tenant / co-resident, move-in / move-out history)
- **Maintenance Requests** — the core entity: a resident-submitted issue tied to a unit,
  tracking lifecycle status (submitted → assigned → in progress → completed / cancelled /
  rejected), with assignment and guarded status transitions

## Features Explicitly Excluded from V1

- Dues billing (invoices, payments, waivers)
- Amenity booking / shared-facility reservations
- Announcements / resident notices
- Payment gateway integration

These are described at a high level in `ASSUMPTIONS_AND_TRADEOFFS.md` so the design isn't
blocked by them later, but no schema or endpoint for them ships in this vertical slice.

## Module Tables (my prefix: `condo_`)

| Table | Purpose |
|---|---|
| `condo_units` | A condo's physical unit inventory |
| `condo_unit_residents` | Links a platform user to a unit as owner/tenant/co-resident |
| `condo_maintenance_requests` | Core entity — a resident-submitted work order tied to a unit |

`organizations` and `users` are **platform tables owned by ARGO**, not part of this module's
deliverable. My sandbox includes a throwaway local stub of both (see `README.md` → "Local
sandbox setup") purely so foreign keys resolve while I develop standalone; that stub is
discarded at integration.

## Assumptions

- One `organization_id` = one condominium corporation (an ARGO tenant)
- A resident is always an existing ARGO platform user; this module stores no separate
  identity records for people — only unit-linkage rows (`condo_unit_residents`)
- Each condo corporation is a separate `organization_id` tenant on the ARGO platform
- The ARGO platform JWT carries `sub` (user id), `org` (organization id), and enough role
  information to resolve permissions — see the open question below

## Open Questions

- Does ARGO's platform JWT include structured permission claims directly, or must this module
  call a centralized permissions service per request?
- Should a unit support multiple concurrent owners (co-ownership), or is a single primary
  owner sufficient for V1? (Current schema allows multiple `condo_unit_residents` rows per
  unit but only one active primary contact — see unique constraint in `ERD.md`.)
- Who can waive or void a dues invoice once dues billing is implemented — Property Manager
  only, or also Staff with a reason code? (Deferred — dues billing is out of scope for V1.)

## Known Limitations

- No automated recurring dues billing engine in V1
- No pagination limit above 100 items per page on list endpoints
- No payment gateway — out of scope for V1
- Single role per user; no multi-role support (matches ARGO platform's existing model)
- Race conditions on simultaneous assign/status-change are guarded at the application layer,
  not with a DB-level optimistic lock — documented as a trade-off in `THREAT_MODEL.md`
