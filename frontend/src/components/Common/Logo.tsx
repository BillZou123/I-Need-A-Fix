import { Link } from "@tanstack/react-router"
import { Activity } from "lucide-react"

import { useTheme } from "@/components/theme-provider"
import { cn } from "@/lib/utils"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === "dark"

  const content =
    variant === "responsive" ? (
      <>
        <div
          className={cn(
            "items-center gap-2 group-data-[collapsible=icon]:hidden inline-flex",
            className,
          )}
        >
          <Activity className={cn("size-5", isDark ? "text-cyan-300" : "text-cyan-700")} />
          <span className="font-semibold tracking-tight">I Need A Fix</span>
        </div>
        <Activity
          aria-label="I Need A Fix"
          className={cn(
            "size-5 hidden group-data-[collapsible=icon]:block",
            isDark ? "text-cyan-300" : "text-cyan-700",
            className,
          )}
        />
      </>
    ) : (
      <div className={cn("inline-flex items-center gap-2", className)}>
        <Activity className={cn("size-5", isDark ? "text-cyan-300" : "text-cyan-700")} />
        {variant === "full" ? <span className="font-semibold tracking-tight">I Need A Fix</span> : null}
      </div>
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
