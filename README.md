# I Need A Fix

 A full-stack medical appointment booking app built with FastAPI + React.

 ## How to run the project

 ### Prerequisites
 - Docker Desktop
 - macOS/Linux hosts entry for local domains (if not already present)

 ### 1) Create your environment file
 From the project root, copy `.env.example` to `.env` and replace all `changethis` values with your own secrets/passwords.

 ### 2) Start the stack
 From the project root:

 ```bash
 docker compose up -d --build
 ```

 ### 3) Open the app
 - Frontend: http://dashboard.localhost
 - Backend API: http://api.localhost

 ### 4) Default admin login
 - Email: `admin@example.com`
 - Password: Your_Password

 All sample doctors and patients share the password `Testpass1!`

 #### Sample doctor logins

 | Role | Name | Email | Password |
 |---|---|---|---|
 | Doctor | Dr. Sarah Chen | dr.chen@ineedafix.dev | Testpass1! |
 | Doctor | Dr. Michael Patel | dr.patel@ineedafix.dev | Testpass1! |
 | Doctor | Dr. Emily Rodriguez | dr.rodriguez@ineedafix.dev | Testpass1! |

 #### Sample patient logins

 | Role | Name | Email | Password |
 |---|---|---|---|
 | Patient | Alice Wong | alice@ineedafix.dev | Testpass1! |
 | Patient | Bob Nguyen | bob@ineedafix.dev | Testpass1! |
 | Patient | Carol Smith | carol@ineedafix.dev | Testpass1! |

 ### 5) Stop the stack
 ```bash
 docker compose down
 ```

 ---

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
