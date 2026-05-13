import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { CalendarCheck2, Stethoscope } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type AppointmentCreate,
  AppointmentsService,
  type DoctorAvailabilityPublic,
  type DoctorPublic,
  DoctorsService,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const bookingFormSchema = z.object({
  patient_name: z.string().min(1, "Patient name is required"),
  patient_email: z.string().email("Please enter a valid email"),
  reason_for_visit: z.string().min(1, "Please share a short reason for visit"),
})

type BookingFormData = z.infer<typeof bookingFormSchema>

export const Route = createFileRoute("/_layout/appointments")({
  component: AppointmentsPage,
  head: () => ({
    meta: [
      {
        title: "Book Appointment - I Need A Fix",
      },
    ],
  }),
})

function formatSlot(slot: DoctorAvailabilityPublic) {
  const start = new Date(slot.start_time)
  const end = new Date(slot.end_time)
  return `${start.toLocaleString()} - ${end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
}

function AppointmentsPage() {
  const { user: currentUser } = useAuth()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const [selectedDoctorId, setSelectedDoctorId] = useState<string>("")
  const [selectedSlotId, setSelectedSlotId] = useState<string>("")

  const form = useForm<BookingFormData>({
    resolver: zodResolver(bookingFormSchema),
    defaultValues: {
      patient_name: currentUser?.full_name || "",
      patient_email: currentUser?.email || "",
      reason_for_visit: "",
    },
  })

  useEffect(() => {
    if (!currentUser) return
    form.setValue("patient_name", currentUser.full_name || "")
    form.setValue("patient_email", currentUser.email)
  }, [currentUser, form])

  const doctorsQuery = useQuery({
    queryKey: ["doctors"],
    queryFn: () => DoctorsService.readDoctors({ skip: 0, limit: 100 }),
  })

  const selectedDoctor = useMemo<DoctorPublic | undefined>(
    () => doctorsQuery.data?.data.find((doctor) => doctor.id === selectedDoctorId),
    [doctorsQuery.data?.data, selectedDoctorId],
  )

  const availabilitiesQuery = useQuery({
    queryKey: ["doctor-availabilities", selectedDoctorId],
    enabled: !!selectedDoctorId,
    queryFn: () =>
      DoctorsService.readDoctorAvailabilities({
        doctorId: selectedDoctorId,
        onlyOpen: true,
      }),
  })

  const createAppointmentMutation = useMutation({
    mutationFn: (payload: AppointmentCreate) =>
      AppointmentsService.createAppointment({ requestBody: payload }),
    onSuccess: () => {
      showSuccessToast("Appointment request submitted")
      setSelectedSlotId("")
      form.setValue("reason_for_visit", "")
      queryClient.invalidateQueries({ queryKey: ["doctor-availabilities", selectedDoctorId] })
      queryClient.invalidateQueries({ queryKey: ["appointments"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (values: BookingFormData) => {
    if (!selectedDoctorId) {
      showErrorToast("Please select a physician")
      return
    }
    if (!selectedSlotId) {
      showErrorToast("Please select an available appointment slot")
      return
    }

    createAppointmentMutation.mutate({
      ...values,
      doctor_id: selectedDoctorId,
      availability_id: selectedSlotId,
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Book an Appointment</h1>
        <p className="text-muted-foreground">
          Choose a physician, pick an available slot, and submit your visit
          details.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Stethoscope className="size-4" />
            1. Choose a physician
          </CardTitle>
          <CardDescription>
            Select the doctor you want to book with.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {doctorsQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading physicians...</p>
          ) : doctorsQuery.data && doctorsQuery.data.data.length > 0 ? (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {doctorsQuery.data.data.map((doctor) => {
                const isActive = doctor.id === selectedDoctorId
                return (
                  <button
                    key={doctor.id}
                    className={`text-left rounded-lg border p-4 transition ${
                      isActive
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/60"
                    }`}
                    onClick={() => {
                      setSelectedDoctorId(doctor.id)
                      setSelectedSlotId("")
                    }}
                    type="button"
                  >
                    <p className="font-medium">{doctor.full_name}</p>
                    <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
                    {doctor.bio ? (
                      <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                        {doctor.bio}
                      </p>
                    ) : null}
                  </button>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No physicians are available yet.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarCheck2 className="size-4" />
            2. Choose an available time
          </CardTitle>
          <CardDescription>
            {selectedDoctor
              ? `Available slots for Dr. ${selectedDoctor.full_name}`
              : "Select a physician first to see open slots"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!selectedDoctorId ? (
            <p className="text-sm text-muted-foreground">No physician selected yet.</p>
          ) : availabilitiesQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading available slots...</p>
          ) : availabilitiesQuery.data && availabilitiesQuery.data.data.length > 0 ? (
            <div className="grid gap-2 md:grid-cols-2">
              {availabilitiesQuery.data.data.map((slot) => (
                <Button
                  key={slot.id}
                  onClick={() => setSelectedSlotId(slot.id)}
                  type="button"
                  variant={selectedSlotId === slot.id ? "default" : "outline"}
                  className="justify-start whitespace-normal h-auto py-3"
                >
                  {formatSlot(slot)}
                </Button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No open slots for this physician right now.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>3. Patient details and reason for visit</CardTitle>
          <CardDescription>
            Submit your details to place the booking request.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="patient_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Patient full name</FormLabel>
                      <FormControl>
                        <Input placeholder="Your full name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="patient_email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="you@example.com"
                          type="email"
                          readOnly
                          className="bg-muted cursor-not-allowed"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="reason_for_visit"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reason for visit</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Describe your symptoms or reason"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <LoadingButton
                type="submit"
                loading={createAppointmentMutation.isPending}
              >
                Request appointment
              </LoadingButton>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
