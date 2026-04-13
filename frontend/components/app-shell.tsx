import Link from "next/link";
import { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Academic Review Platform</p>
          <h1>ConfEval</h1>
        </div>
        <nav>
          <Link href="/">Overview</Link>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/dashboard/notifications">Notifications</Link>
          <Link href="/dashboard/catalog">Catalog</Link>
          <Link href="/dashboard/student/projects">Projects</Link>
          <Link href="/dashboard/student/team-invitations">Team Invitations</Link>
          <Link href="/dashboard/reviewer/sessions">Reviewer Sessions</Link>
          <Link href="/dashboard/reviewer/assignments">Reviewer Assignments</Link>
          <Link href="/dashboard/admin/tags">Tags</Link>
          <Link href="/dashboard/admin/conferences">Conferences</Link>
          <Link href="/dashboard/admin/sessions">Sessions</Link>
          <Link href="/dashboard/admin/applications">Application Queue</Link>
          <Link href="/dashboard/admin/assignments">Reviewer Assignment Queue</Link>
          <Link href="/dashboard/admin/projects">Admin Project Queue</Link>
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
