import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Appointment,
    AppointmentCreate,
    AppointmentStatus,
    Doctor,
    DoctorAvailability,
    DoctorAvailabilityCreate,
    DoctorCreate,
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserRoleUpdate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def _seed_doctor_availability(*, session: Session, doctor: Doctor) -> None:
    """Create 30-min slots 9-12 and 14-17 for the next 7 days."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    base = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if base <= now:
        base += datetime.timedelta(days=1)
    for day_offset in range(7):
        day_start = base + datetime.timedelta(days=day_offset)
        for hour in [9, 10, 11, 14, 15, 16]:
            slot_start = day_start.replace(hour=hour)
            slot_end = slot_start + datetime.timedelta(minutes=30)
            session.add(
                DoctorAvailability(
                    doctor_id=doctor.id,
                    start_time=slot_start,
                    end_time=slot_end,
                    is_booked=False,
                )
            )


def update_user_role(*, session: Session, db_user: User, role_in: UserRoleUpdate) -> User:
    from app.models import UserRole  # avoid circular at module level
    previous_role = db_user.role
    db_user.role = role_in.role
    session.add(db_user)

    # Auto-manage Doctor profile
    if role_in.role == UserRole.doctor:
        # Create a Doctor profile + availability slots if one doesn't exist yet
        existing = get_doctor_by_user_id(session=session, user_id=db_user.id)
        if not existing:
            doctor = Doctor(
                full_name=db_user.full_name or db_user.email,
                specialty="General",
                bio="",
                user_id=db_user.id,
            )
            session.add(doctor)
            session.flush()  # get doctor.id
            _seed_doctor_availability(session=session, doctor=doctor)
    elif previous_role == UserRole.doctor:
        # Remove Doctor profile and availability when role is changed away from doctor
        existing = get_doctor_by_user_id(session=session, user_id=db_user.id)
        if existing:
            session.exec(  # type: ignore
                __import__("sqlmodel", fromlist=["select"]).select(DoctorAvailability).where(
                    DoctorAvailability.doctor_id == existing.id
                )
            )
            from sqlmodel import select as _select, delete as _delete
            session.exec(_delete(DoctorAvailability).where(DoctorAvailability.doctor_id == existing.id))  # type: ignore
            session.delete(existing)

    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_doctor(*, session: Session, doctor_in: DoctorCreate) -> Doctor:
    db_doctor = Doctor.model_validate(doctor_in)
    session.add(db_doctor)
    session.commit()
    session.refresh(db_doctor)
    return db_doctor


def get_doctors(*, session: Session, skip: int = 0, limit: int = 100) -> list[Doctor]:
    statement = select(Doctor).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_doctor_by_user_id(*, session: Session, user_id: uuid.UUID) -> Doctor | None:
    statement = select(Doctor).where(Doctor.user_id == user_id)
    return session.exec(statement).first()


def create_doctor_availability(
    *, session: Session, availability_in: DoctorAvailabilityCreate
) -> DoctorAvailability:
    db_availability = DoctorAvailability.model_validate(availability_in)
    session.add(db_availability)
    session.commit()
    session.refresh(db_availability)
    return db_availability


def get_doctor_availabilities(
    *, session: Session, doctor_id: uuid.UUID, only_open: bool = True
) -> list[DoctorAvailability]:
    statement = select(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor_id)
    if only_open:
        statement = statement.where(DoctorAvailability.is_booked.is_(False))
    statement = statement.order_by(DoctorAvailability.start_time)
    return list(session.exec(statement).all())


def create_appointment(*, session: Session, appointment_in: AppointmentCreate) -> Appointment:
    availability = session.get(DoctorAvailability, appointment_in.availability_id)
    if availability is None:
        raise ValueError("Availability slot not found")
    if availability.is_booked:
        raise ValueError("Availability slot already booked")
    if availability.doctor_id != appointment_in.doctor_id:
        raise ValueError("Availability slot does not belong to selected doctor")

    db_appointment = Appointment.model_validate(
        appointment_in,
        update={"appointment_time": availability.start_time},
    )
    session.add(db_appointment)
    availability.is_booked = True
    session.add(availability)
    session.commit()
    session.refresh(db_appointment)
    return db_appointment


def get_appointments(
    *,
    session: Session,
    doctor_id: uuid.UUID | None = None,
    patient_email: str | None = None,
    status: AppointmentStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Appointment]:
    statement = select(Appointment)
    if doctor_id is not None:
        statement = statement.where(Appointment.doctor_id == doctor_id)
    if patient_email is not None:
        statement = statement.where(Appointment.patient_email == patient_email)
    if status is not None:
        statement = statement.where(Appointment.status == status)
    statement = statement.order_by(Appointment.appointment_time).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_appointment_status(
    *, session: Session, appointment: Appointment, status: AppointmentStatus
) -> Appointment:
    appointment.status = status
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment
