import datetime

from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Doctor, DoctorAvailability, User, UserCreate, UserRole

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    doctor_count = len(session.exec(select(Doctor)).all())
    if doctor_count > 0:
        return

    # ── Demo doctor users ──────────────────────────────────────────────────────
    demo_doctor_specs = [
        {
            "full_name": "Dr. Sarah Chen",
            "specialty": "Family Medicine",
            "bio": "Focused on preventive care and general wellness.",
            "email": "dr.chen@ineedafix.dev",
        },
        {
            "full_name": "Dr. Michael Patel",
            "specialty": "Orthopedics",
            "bio": "Experienced in joint pain and sports injury treatment.",
            "email": "dr.patel@ineedafix.dev",
        },
        {
            "full_name": "Dr. Emily Rodriguez",
            "specialty": "Dermatology",
            "bio": "Specializes in skin conditions and long-term care plans.",
            "email": "dr.rodriguez@ineedafix.dev",
        },
    ]

    # ── Demo patient users ─────────────────────────────────────────────────────
    demo_patient_specs = [
        {"full_name": "Alice Wong", "email": "alice@ineedafix.dev"},
        {"full_name": "Bob Nguyen", "email": "bob@ineedafix.dev"},
        {"full_name": "Carol Smith", "email": "carol@ineedafix.dev"},
    ]

    _demo_password = "Testpass1!"  # noqa: S105

    for spec in demo_patient_specs:
        if not session.exec(select(User).where(User.email == spec["email"])).first():
            crud.create_user(
                session=session,
                user_create=UserCreate(
                    email=spec["email"],
                    full_name=spec["full_name"],
                    password=_demo_password,
                    is_superuser=False,
                ),
            )
            # assign patient role
            patient_user = session.exec(select(User).where(User.email == spec["email"])).first()
            if patient_user:
                patient_user.role = UserRole.patient
                session.add(patient_user)

    session.flush()

    start_base = datetime.datetime.now(datetime.timezone.utc).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    if start_base <= datetime.datetime.now(datetime.timezone.utc):
        start_base = start_base + datetime.timedelta(days=1)

    for spec in demo_doctor_specs:
        # create user account for doctor if it doesn't exist
        if not session.exec(select(User).where(User.email == spec["email"])).first():
            crud.create_user(
                session=session,
                user_create=UserCreate(
                    email=spec["email"],
                    full_name=spec["full_name"],
                    password=_demo_password,
                    is_superuser=False,
                ),
            )
        doctor_user = session.exec(select(User).where(User.email == spec["email"])).first()
        if doctor_user:
            doctor_user.role = UserRole.doctor
            session.add(doctor_user)
            session.flush()

        # create doctor profile linked to the user
        doctor = Doctor(
            full_name=spec["full_name"],
            specialty=spec["specialty"],
            bio=spec["bio"],
            user_id=doctor_user.id if doctor_user else None,
        )
        session.add(doctor)
        session.flush()

        for day_offset in range(3):
            day_start = start_base + datetime.timedelta(days=day_offset)
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

    session.commit()
