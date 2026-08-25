"""
Role -> permission map. Mirrors docs/RBAC_MATRIX.md exactly.
"""

ROLE_PERMISSIONS = {
    'resident': {'maintenance.view', 'maintenance.create', 'maintenance.update_status', 'unit.view'},
    'staff':    {'maintenance.view', 'maintenance.create', 'maintenance.assign',
                 'maintenance.update_status', 'unit.view',
                 'user.view', 'assignment.view'},
    'manager':  {'maintenance.view', 'maintenance.create', 'maintenance.assign',
                 'maintenance.update_status', 'maintenance.delete', 'unit.view', 'unit.manage',
                 'user.view', 'assignment.view', 'assignment.manage'},
    'admin':    {'maintenance.view', 'maintenance.create', 'maintenance.assign',
                 'maintenance.update_status', 'maintenance.delete', 'unit.view', 'unit.manage',
                 'user.view', 'user.manage', 'assignment.view', 'assignment.manage'},
}


def role_has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
