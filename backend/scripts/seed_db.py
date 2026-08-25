"""
Seeds the local sandbox stub with a demo org, 4 demo users, sample units, a resident-unit
link, and one sample maintenance request.

Run after creating tables:
    python -m scripts.seed_db
"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models._local_stub_platform_tables import LocalStubOrganization, LocalStubUser
from app.models.condo_units import CondoUnit
from app.models.condo_unit_residents import CondoUnitResident
from app.models.condo_maintenance_requests import CondoMaintenanceRequest
from app.core.security import hash_password
from datetime import datetime


def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        org = db.query(LocalStubOrganization).filter_by(name='Utrera Condos Corporation').first()
        if org is None:
            org = LocalStubOrganization(id=uuid.uuid4(), name='Utrera Condos Corporation')
            db.add(org)
            db.commit()
            print(f'Created organization: {org.id}')

        demo_users = [
            ('Alice Administrator', 'admin@condo.test', 'admin'),
            ('Peter Manager', 'manager@condo.test', 'manager'),
            ('Fiona FrontDesk', 'staff@condo.test', 'staff'),
            ('Ramon Resident', 'resident@condo.test', 'resident'),
        ]
        created = {}
        for full_name, email, role in demo_users:
            user = db.query(LocalStubUser).filter_by(email=email).first()
            if user is None:
                user = LocalStubUser(
                    id=uuid.uuid4(), organization_id=org.id, full_name=full_name,
                    email=email, password_hash=hash_password('Password123!'), role=role,
                )
                db.add(user)
                db.commit()
                print(f'Created user: {email} ({role})')
            created[role] = user

        unit = db.query(CondoUnit).filter_by(organization_id=org.id, unit_number='101', building='Tower A').first()
        if unit is None:
            unit = CondoUnit(id=uuid.uuid4(), organization_id=org.id, unit_number='101',
                              building='Tower A', floor=1, status='occupied', created_by=created['admin'].id)
            db.add(unit)
            db.commit()
            print(f'Created unit: {unit.id}')

        for number, building, floor, status_ in [
            ('102', 'Tower A', 1, 'vacant'),
            ('201', 'Tower A', 2, 'under_maintenance'),
            ('301', 'Tower B', 3, 'vacant'),
        ]:
            existing = db.query(CondoUnit).filter_by(organization_id=org.id, unit_number=number, building=building).first()
            if existing is None:
                db.add(CondoUnit(id=uuid.uuid4(), organization_id=org.id, unit_number=number,
                                  building=building, floor=floor, status=status_, created_by=created['admin'].id))
        db.commit()

        link = db.query(CondoUnitResident).filter_by(unit_id=unit.id, user_id=created['resident'].id).first()
        if link is None:
            link = CondoUnitResident(
                id=uuid.uuid4(), organization_id=org.id, unit_id=unit.id, user_id=created['resident'].id,
                relationship_type='owner', is_primary_contact=True, moved_in_at=datetime.utcnow(),
                created_by=created['admin'].id,
            )
            db.add(link)
            db.commit()
            print('Linked resident to unit 101.')

        sample = db.query(CondoMaintenanceRequest).filter_by(unit_id=unit.id, category='plumbing').first()
        if sample is None:
            sample = CondoMaintenanceRequest(
                id=uuid.uuid4(), organization_id=org.id, unit_id=unit.id, requested_by=created['resident'].id,
                assigned_to=created['staff'].id, category='plumbing',
                description='Kitchen faucet has been leaking for two days.',
                priority='medium', status='assigned',
                created_by=created['resident'].id, updated_by=created['staff'].id,
            )
            db.add(sample)
            db.commit()
            print('Created sample maintenance request.')

        print('\nSeeding complete. Demo accounts (password: Password123!):')
        for _, email, role in demo_users:
            print(f'  {email:25s} -> {role}')
        print(f'\nOrganization ID: {org.id}')
        for role, user in created.items():
            print(f'  {role} user id: {user.id}')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
