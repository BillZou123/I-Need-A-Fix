import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Appointment,
    AppointmentCreate,
    AppointmentPublic,
    AppointmentsPublic,
    AppointmentStatus,
    AppointmentUpdateStatus,
    Doctor,
    UserRole,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=AppointmentsPublic)
def read_appointments(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    doctor_id: uuid.UUID | None = None,
    status: AppointmentStatus | None = None,
) -> Any:
    """
    Retrieve appointments.
    Superusers can see all appointments; regular users see only their own by email.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Appointment)
        if doctor_id is not None:
            count_statement = count_statement.where(Appointment.doctor_id == doctor_id)
        if status is not None:
            count_statement = count_statement.where(Appointment.status == status)
        count = session.exec(count_statement).one()
        appointments = crud.get_appointments(
            session=session,
            doctor_id=doctor_id,
            status=status,
            skip=skip,
            limit=limit,
        )
    elif current_user.role == UserRole.patient:
        count_statement = select(func.count()).select_from(Appointment).where(
            Appointment.patient_email == current_user.email
        )
        if doctor_id is not None:
            count_statement = count_statement.where(Appointment.doctor_id == doctor_id)
        if status is not None:
            count_statement = count_statement.where(Appointment.status == status)
        count = session.exec(count_statement).one()
        appointments = crud.get_appointments(
            session=session,
            doctor_id=doctor_id,
            patient_email=current_user.email,
            status=status,
            skip=skip,
            limit=limit,
        )
    elif current_user.role == UserRole.doctor:
        doctor_profile = crud.get_doctor_by_user_id(session=session, user_id=current_user.id)
        if not doctor_profile:
            return AppointmentsPublic(data=[], count=0)

        if doctor_id is not None and doctor_id != doctor_profile.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        count_statement = (
            select(func.count())
            .select_from(Appointment)
            .where(Appointment.doctor_id == doctor_profile.id)
        )
        if status is not None:
            count_statement = count_statement.where(Appointment.status == status)
        count = session.exec(count_statement).one()
        appointments = crud.get_appointments(
            session=session,
            doctor_id=doctor_profile.id,
            status=status,
            skip=skip,
            limit=limit,
        )
    else:
        raise HTTPException(status_code=403, detail="Role not assigned")

    data = [AppointmentPublic.model_validate(a) for a in appointments]
    return AppointmentsPublic(data=data, count=count)


@router.get("/{appointment_id}", response_model=AppointmentPublic)
def read_appointment(
    session: SessionDep,
    current_user: CurrentUser,
    appointment_id: uuid.UUID,
) -> Any:
    """
    Get one appointment by ID.
    """
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.is_superuser:
        return appointment

    if current_user.role == UserRole.patient:
        if appointment.patient_email != current_user.email:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return appointment

    if current_user.role == UserRole.doctor:
        doctor_profile = crud.get_doctor_by_user_id(session=session, user_id=current_user.id)
        if not doctor_profile or appointment.doctor_id != doctor_profile.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return appointment

    raise HTTPException(status_code=403, detail="Role not assigned")


@router.post("/", response_model=AppointmentPublic)
def create_appointment(
    *, session: SessionDep, current_user: CurrentUser, appointment_in: AppointmentCreate
) -> Any:
    """
    Request/book an appointment.
    """
    if not current_user.is_superuser:
        if current_user.role != UserRole.patient:
            raise HTTPException(status_code=403, detail="Only patients can book appointments")
        if appointment_in.patient_email != current_user.email:
            raise HTTPException(status_code=403, detail="Patients can only book for themselves")

    doctor = session.get(Doctor, appointment_in.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    try:
        appointment = crud.create_appointment(session=session, appointment_in=appointment_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return appointment


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentPublic,
)
def update_appointment_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appointment_id: uuid.UUID,
    status_in: AppointmentUpdateStatus,
) -> Any:
    """
    Update appointment status (admin/physician).
    """
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if not current_user.is_superuser:
        if current_user.role != UserRole.doctor:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        doctor_profile = crud.get_doctor_by_user_id(session=session, user_id=current_user.id)
        if not doctor_profile or doctor_profile.id != appointment.doctor_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return crud.update_appointment_status(
        session=session,
        appointment=appointment,
        status=status_in.status,
    )
