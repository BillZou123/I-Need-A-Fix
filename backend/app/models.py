import datetime
import enum
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel



#The pattern of this models.py is like this:
# Base model
#     shared fields

# Create model
#     fields required when creating

# Update model
#     fields allowed when updating, usually optional

# Database model
#     table=True, actual DB table, has id / foreign keys / relationships

# Public model
#     safe response returned to frontend





# Shared properties
class UserBase(SQLModel): #this is not a database table itself, it is just a calss that can be reused.
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase): #This inherits from UserBase, so it has all the same fields as UserBase, but we can add additional fields that are required for user creation. In this case, we add a password field that is required when creating a new user.
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel): #this is not inherited from Userbase, because we want to allow users to register without providing is_active, is_superuser, etc. We only require email, password, and optionally full_name.
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    #here, we override the 2 fileds from UserBase to make them optional, because when updating a user, we may not want to update all fields. For example, we may only want to update the full_name, but not the email or is_active status. By making them optional, we can allow partial updates to the user.
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    #define the request body for updating password, it requires the current password and the new password. 
    #we don't allow None for these fields, because when updating password, both current password and new password are required. We want to make sure that the user provides both fields when updating their password.
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserRole(str, enum.Enum):
    doctor = "doctor"
    patient = "patient"


class UserRoleUpdate(SQLModel):
    role: UserRole


# Database model, database table inferred from class name
class User(UserBase, table=True): #table = True means this is a database table, and the table name will be inferred from the class name (in this case, "user"). This class inherits from UserBase, so it has all the fields defined in UserBase, but we can also add additional fields that are specific to the database model. In this case, we add an id field that is a UUID and is the primary key for the user table. We also add a hashed_password field to store the hashed version of the user's password, and a relationship to the Item model to represent the items owned by the user.
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    role: UserRole | None = Field(default=None)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    doctor_profile: "Doctor" = Relationship(back_populates="user")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    role: UserRole | None = None

#This is a response wrapper for returning multiple users.
#Example API response:
# {
#   "data": [
#     {
#       "id": "some-uuid",
#       "email": "admin@example.com",
#       "is_active": true,
#       "is_superuser": true,
#       "full_name": "Admin"
#     }
#   ],
#   "count": 1
# }
class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # when updating an item, we wanna makew title optional, because maybe we only want to update the description, but not the title. By making it optional, we can allow partial updates to the item.


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items") #this is the relationship to the User model, it allows us to access the owner of the item by using item.owner. The back_populates="items" means that we can also access the items owned by a user by using user.items. The cascade_delete=True means that when a user is deleted, all items owned by that user will also be deleted automatically by the database, which helps maintain data integrity and prevents orphaned records in the items table.


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID

#the wrapper for multiple items.
#example API response:
# {
#   "data": [
#     {
#       "id": "some-uuid",
#       "title": "Item 1",
#       "description": "This is item 1",
#       "owner_id": "some-user-uuid"
#     },
#    {
#      "id": "some-uuid",
#      "title": "Item 2",
#      "description": "This is item 2",
#    "owner_id": "some-user-uuid"
#  ],
#  "count": 2
# }         
class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class DoctorBase(SQLModel):
    full_name: str = Field(min_length=1, max_length=255)
    specialty: str = Field(min_length=1, max_length=255)
    bio: str | None = Field(default=None, max_length=500)


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(SQLModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    specialty: str | None = Field(default=None, min_length=1, max_length=255)
    bio: str | None = Field(default=None, max_length=500)


class Doctor(DoctorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", unique=True)
    availabilities: list["DoctorAvailability"] = Relationship(back_populates="doctor")
    appointments: list["Appointment"] = Relationship(back_populates="doctor")
    user: User | None = Relationship(back_populates="doctor_profile")


class DoctorPublic(DoctorBase):
    id: uuid.UUID


class DoctorsPublic(SQLModel):
    data: list[DoctorPublic]
    count: int


class DoctorAvailabilityBase(SQLModel):
    start_time: datetime.datetime
    end_time: datetime.datetime


class DoctorAvailabilityCreate(DoctorAvailabilityBase):
    doctor_id: uuid.UUID


class DoctorAvailabilityUpdate(SQLModel):
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    is_booked: bool | None = None


class DoctorAvailability(DoctorAvailabilityBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    doctor_id: uuid.UUID = Field(foreign_key="doctor.id", nullable=False, ondelete="CASCADE")
    is_booked: bool = Field(default=False)
    doctor: Doctor | None = Relationship(back_populates="availabilities")
    appointment: "Appointment" = Relationship(back_populates="availability")


class DoctorAvailabilityPublic(DoctorAvailabilityBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    is_booked: bool


class DoctorAvailabilitiesPublic(SQLModel):
    data: list[DoctorAvailabilityPublic]
    count: int


class AppointmentBase(SQLModel):
    patient_name: str = Field(min_length=1, max_length=255)
    patient_email: EmailStr = Field(max_length=255)
    reason_for_visit: str | None = Field(default=None, max_length=1000)


class AppointmentCreate(AppointmentBase):
    doctor_id: uuid.UUID
    availability_id: uuid.UUID


class AppointmentUpdateStatus(SQLModel):
    status: AppointmentStatus


class Appointment(AppointmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    doctor_id: uuid.UUID = Field(foreign_key="doctor.id", nullable=False, ondelete="CASCADE")
    availability_id: uuid.UUID = Field(
        foreign_key="doctoravailability.id", nullable=False, unique=True, index=True
    )
    appointment_time: datetime.datetime
    status: AppointmentStatus = Field(default=AppointmentStatus.pending)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    doctor: Doctor | None = Relationship(back_populates="appointments")
    availability: DoctorAvailability | None = Relationship(back_populates="appointment")


class AppointmentPublic(AppointmentBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    availability_id: uuid.UUID
    appointment_time: datetime.datetime
    status: AppointmentStatus
    created_at: datetime.datetime


class AppointmentsPublic(SQLModel):
    data: list[AppointmentPublic]
    count: int
