import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"

import { type UserPublic, type UserRole, UsersService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select"
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

export const Route = createFileRoute("/_layout/admin/users")({
	component: AdminUsers,
	head: () => ({
		meta: [
			{
				title: "Admin Users - I Need A Fix",
			},
		],
	}),
})

function roleLabel(user: UserPublic) {
	if (user.is_superuser) return "Superuser"
	if (user.role === "doctor") return "Doctor"
	if (user.role === "patient") return "Patient"
	return "Unassigned"
}

function AdminUsers() {
	const navigate = useNavigate()
	const { user: currentUser, userIsLoading } = useAuth()
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	useEffect(() => {
		if (!userIsLoading && !currentUser?.is_superuser) {
			navigate({ to: "/" })
		}
	}, [currentUser?.is_superuser, navigate, userIsLoading])

	const { data: usersData, isLoading } = useQuery({
		queryKey: ["users"],
		queryFn: () => UsersService.readUsers({ skip: 0, limit: 200 }),
		enabled: !!currentUser?.is_superuser,
	})

	const updateRoleMutation = useMutation({
		mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
			UsersService.updateUserRole({
				userId,
				requestBody: { role },
			}),
		onSuccess: () => {
			showSuccessToast("User role updated")
			queryClient.invalidateQueries({ queryKey: ["users"] })
			queryClient.invalidateQueries({ queryKey: ["currentUser"] })
		},
		onError: handleError.bind(showErrorToast),
	})

	const users = usersData?.data ?? []

	if (userIsLoading) {
		return <div className="text-muted-foreground">Loading...</div>
	}

	return (
		<div className="flex flex-col gap-6">
			<div>
				<h1 className="text-2xl font-bold tracking-tight">Admin Users</h1>
				<p className="text-muted-foreground">
					Assign each registered user as a doctor or patient.
				</p>
			</div>

			<Card>
				<CardContent className="pt-6">
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead>Name</TableHead>
								<TableHead>Email</TableHead>
								<TableHead>Current Role</TableHead>
								<TableHead>Assign Role</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{isLoading ? (
								<TableRow>
									<TableCell colSpan={4} className="text-center text-muted-foreground">
										Loading users...
									</TableCell>
								</TableRow>
							) : users.length === 0 ? (
								<TableRow>
									<TableCell colSpan={4} className="text-center text-muted-foreground">
										No users found.
									</TableCell>
								</TableRow>
							) : (
								users.map((user) => {
									const canEdit = !user.is_superuser
									return (
										<TableRow key={user.id}>
											<TableCell>{user.full_name || "N/A"}</TableCell>
											<TableCell>{user.email}</TableCell>
											<TableCell>
												<Badge variant={user.is_superuser ? "default" : "secondary"}>
													{roleLabel(user)}
												</Badge>
											</TableCell>
											<TableCell>
												{canEdit ? (
													<Select
														value={user.role ?? undefined}
														onValueChange={(value) => {
															updateRoleMutation.mutate({
																userId: user.id,
																role: value as UserRole,
															})
														}}
													>
														<SelectTrigger className="w-[160px]">
															<SelectValue placeholder="Select role" />
														</SelectTrigger>
														<SelectContent>
															<SelectItem value="patient">Patient</SelectItem>
															<SelectItem value="doctor">Doctor</SelectItem>
														</SelectContent>
													</Select>
												) : (
													<span className="text-sm text-muted-foreground">Not editable</span>
												)}
											</TableCell>
										</TableRow>
									)
								})
							)}
						</TableBody>
					</Table>
				</CardContent>
			</Card>
		</div>
	)
}
