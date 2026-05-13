import { CalendarDays, ClipboardList, Home, Users } from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const dashboardItem: Item = { icon: Home, title: "Dashboard", path: "/" }

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  let items: Item[]
  if (currentUser?.is_superuser) {
    items = [
      dashboardItem,
      { icon: ClipboardList, title: "Manage Bookings", path: "/bookings" },
      { icon: Users, title: "Admin", path: "/admin/users" },
    ]
  } else if (currentUser?.role === "doctor") {
    items = [
      dashboardItem,
      { icon: ClipboardList, title: "My Schedule", path: "/bookings" },
    ]
  } else if (currentUser?.role === "patient") {
    items = [
      dashboardItem,
      { icon: CalendarDays, title: "Book Appointment", path: "/appointments" },
      { icon: ClipboardList, title: "My Bookings", path: "/bookings" },
    ]
  } else {
    // unassigned — just dashboard
    items = [dashboardItem]
  }

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
