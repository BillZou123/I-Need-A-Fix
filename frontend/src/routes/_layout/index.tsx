import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { CalendarDays, ClipboardList, Stethoscope, Users } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - I Need A Fix",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const isSuperuser = !!currentUser?.is_superuser
  const role = currentUser?.role

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground">
          Welcome to I Need A Fix — your appointment workspace.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* ── Superuser cards ──────────────────────────────── */}
        {isSuperuser && (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <ClipboardList className="size-5" />
                  Manage bookings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Review all patient appointments and confirm or cancel requests.
                </p>
                <Button asChild>
                  <RouterLink to="/bookings">Open bookings</RouterLink>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="size-5" />
                  Assign user roles
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Designate registered users as doctors or patients.
                </p>
                <Button variant="outline" asChild>
                  <RouterLink to="/admin/users">Open admin panel</RouterLink>
                </Button>
              </CardContent>
            </Card>
          </>
        )}

        {/* ── Doctor cards ─────────────────────────────────── */}
        {!isSuperuser && role === "doctor" && (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Stethoscope className="size-5" />
                  My appointments
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  View upcoming patient appointments assigned to you.
                </p>
                <Button asChild>
                  <RouterLink to="/bookings">View schedule</RouterLink>
                </Button>
              </CardContent>
            </Card>
          </>
        )}

        {/* ── Patient cards ────────────────────────────────── */}
        {!isSuperuser && role === "patient" && (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <CalendarDays className="size-5" />
                  Book appointment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Choose a physician, pick an available slot, and submit your visit reason.
                </p>
                <Button asChild>
                  <RouterLink to="/appointments">Start booking</RouterLink>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <ClipboardList className="size-5" />
                  My bookings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Track your upcoming appointments and their current status.
                </p>
                <Button variant="outline" asChild>
                  <RouterLink to="/bookings">Open bookings</RouterLink>
                </Button>
              </CardContent>
            </Card>
          </>
        )}

        {/* ── Unassigned users ────────────────────────────── */}
        {!isSuperuser && !role && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Pending role assignment</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Your account is set up but hasn't been assigned a role yet. Please
                contact the administrator to get access as a doctor or patient.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
