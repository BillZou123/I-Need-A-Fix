import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/admin")({
  component: AdminLayout,
  head: () => ({
    meta: [
      {
        title: "Admin - I Need A Fix",
      },
    ],
  }),
})

function AdminLayout() {
  return <Outlet />
}
