import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Doctor,
    DoctorAvailabilitiesPublic,
    DoctorAvailability,
    DoctorAvailabilityCreate,
    DoctorAvailabilityPublic,
    DoctorCreate,
    DoctorPublic,
    DoctorsPublic,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/", response_model=DoctorsPublic)
def read_doctors(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve doctors.
    """
    count_statement = select(func.count()).select_from(Doctor)
    count = session.exec(count_statement).one()
    doctors = crud.get_doctors(session=session, skip=skip, limit=limit)
    return DoctorsPublic(data=doctors, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=DoctorPublic,
)
def create_doctor(*, session: SessionDep, doctor_in: DoctorCreate) -> Any:
    """
    Create a new doctor profile (admin only).
    """
    return crud.create_doctor(session=session, doctor_in=doctor_in)


@router.get("/{doctor_id}/availabilities", response_model=DoctorAvailabilitiesPublic)
def read_doctor_availabilities(
    session: SessionDep,
    doctor_id: uuid.UUID,
    only_open: bool = True,
) -> Any:
    """
    Retrieve doctor availability slots.
    """
    doctor = session.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    count_statement = select(func.count()).select_from(DoctorAvailability).where(
        DoctorAvailability.doctor_id == doctor_id
    )
    if only_open:
        count_statement = count_statement.where(DoctorAvailability.is_booked.is_(False))
    count = session.exec(count_statement).one()

    availabilities = crud.get_doctor_availabilities(
        session=session,
        doctor_id=doctor_id,
        only_open=only_open,
    )
    data = [DoctorAvailabilityPublic.model_validate(a) for a in availabilities]
    return DoctorAvailabilitiesPublic(data=data, count=count)


@router.post(
    "/availabilities",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=DoctorAvailabilityPublic,
)
def create_doctor_availability(
    *, session: SessionDep, availability_in: DoctorAvailabilityCreate
) -> Any:
    """
    Create a new availability slot for a doctor (admin only).
    """
    doctor = session.get(Doctor, availability_in.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if availability_in.end_time <= availability_in.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    return crud.create_doctor_availability(session=session, availability_in=availability_in)
