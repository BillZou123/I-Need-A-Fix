import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import {
  type AppointmentPublic,
  AppointmentsService,
  type AppointmentStatus,
} from "@/client"
import { DoctorsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/bookings")({
  component: BookingsPage,
  head: () => ({
    meta: [{ title: "Manage Bookings - I Need A Fix" }],
  }),
})

function statusVariant(status: AppointmentStatus) {
  if (status === "confirmed") return "default"
  if (status === "cancelled") return "destructive"
  return "secondary"
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString()
}

function BookingsPage() {
  const { user: currentUser } = useAuth()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const bookingsQuery = useQuery({
    queryKey: ["appointments"],
    queryFn: () => AppointmentsService.readAppointments({ skip: 0, limit: 100 }),
  })

  const doctorsQuery = useQuery({
    queryKey: ["doctors"],
    queryFn: () => DoctorsService.readDoctors({ skip: 0, limit: 200 }),
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ appointmentId, status }: { appointmentId: string; status: AppointmentStatus }) =>
      AppointmentsService.updateAppointmentStatus({
        appointmentId,
        requestBody: { status },
      }),
    onSuccess: () => {
      showSuccessToast("Booking status updated")
      queryClient.invalidateQueries({ queryKey: ["appointments"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const canManage = currentUser?.is_superuser || currentUser?.role === "doctor"

  const appointments = (bookingsQuery.data?.data || []) as AppointmentPublic[]
  const doctorNameById = new Map(
    (doctorsQuery.data?.data ?? []).map((doctor) => [doctor.id, doctor.full_name]),
  )

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Upcoming Bookings</h1>
        <p className="text-muted-foreground">
          {currentUser?.is_superuser
            ? "Review and manage all patient bookings."
            : currentUser?.role === "doctor"
              ? "Confirm or cancel appointments from your patients."
              : "View your own appointment bookings."}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Bookings</CardTitle>
          <CardDescription>
            Booking statuses: pending, confirmed, cancelled.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {bookingsQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading bookings...</p>
          ) : appointments.length === 0 ? (
            <p className="text-sm text-muted-foreground">No bookings found yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patient</TableHead>
                  <TableHead>Doctor</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Appointment time</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Status</TableHead>
                  {canManage ? <TableHead>Actions</TableHead> : null}
                </TableRow>
              </TableHeader>
              <TableBody>
                {appointments.map((booking) => (
                  <TableRow key={booking.id}>
                    <TableCell className="font-medium">{booking.patient_name}</TableCell>
                    <TableCell>
                      {doctorNameById.get(booking.doctor_id) ?? "Unknown doctor"}
                    </TableCell>
                    <TableCell>{booking.patient_email}</TableCell>
                    <TableCell>{formatDateTime(booking.appointment_time)}</TableCell>
                    <TableCell className="max-w-xs truncate">
                      {booking.reason_for_visit || "-"}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant(booking.status)}>{booking.status}</Badge>
                    </TableCell>
                    {canManage ? (
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() =>
                              updateStatusMutation.mutate({
                                appointmentId: booking.id,
                                status: "confirmed",
                              })
                            }
                            disabled={
                              updateStatusMutation.isPending || booking.status === "confirmed"
                            }
                          >
                            Confirm
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              updateStatusMutation.mutate({
                                appointmentId: booking.id,
                                status: "cancelled",
                              })
                            }
                            disabled={
                              updateStatusMutation.isPending || booking.status === "cancelled"
                            }
                          >
                            Cancel
                          </Button>
                        </div>
                      </TableCell>
                    ) : null}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
