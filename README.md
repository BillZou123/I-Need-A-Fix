

 ## What I built

 This project implements a role-based appointment workflow:

 - **Patient flow**
   - Patient can sign up/login
   - Patient can choose a doctor
   - Patient can select from available time slots
   - Patient can submit booking details (`name`, `email`, `reason for visit`)
   - Patient can view their bookings

 - **Doctor/Admin flow**
   - Doctor can view their upcoming bookings
   - Admin can view all bookings
   - Admin/Doctor can update booking status

 - **Booking status lifecycle**
   - `pending`
   - `confirmed`
   - `cancelled`

 - **RBAC**
   - Superuser can assign user roles (`doctor`, `patient`)
   - Backend enforces access based on role

 ---

 ## Key technical/product decisions

 - **Backend:** FastAPI + SQLModel + PostgreSQL
   - Fast, typed API development with clear schema models.
 - **Frontend:** React + TypeScript + TanStack Router/Query
   - Type-safe routing and reliable data fetching/caching.
 - **OpenAPI-generated client**
   - Frontend API calls are generated from backend schema to reduce contract drift.
 - **Role-based filtering done server-side**
   - Prevents overexposure of appointment data to unauthorized users.
 - **Doctor profile and availability model**
   - Separate `Doctor` and `DoctorAvailability` entities to support scheduling and slot booking.
 - **Docker-first runtime**
   - Consistent local environment using compose services and local domains.

 ---

 ## What I would improve with more time

 - Add a dedicated doctor availability management UI (create/edit recurring schedules).
 - Add pagination, filtering, and search for large booking lists.
 - Add stronger audit logs for role changes and status updates.
 - Add notifications (email/in-app) for booking confirmations/cancellations.
 - Improve test coverage for end-to-end role workflows.
 - Add calendar integration (Google/Outlook export/sync).
