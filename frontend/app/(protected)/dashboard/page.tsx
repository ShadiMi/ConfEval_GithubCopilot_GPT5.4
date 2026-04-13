import { getSessionUser } from "@/lib/auth";

const roleMessages: Record<string, string> = {
  student: "Your dashboard will center on project submissions, attachments, team invitations, and completed reviews.",
  internal_reviewer: "Your dashboard will center on session applications, assigned projects, and review drafting.",
  external_reviewer: "Your dashboard will center on assigned sessions, projects, and approval-sensitive access.",
  admin: "Your dashboard will center on approvals, conferences, sessions, criteria, assignments, reports, and settings.",
};

export default async function DashboardPage() {
  const sessionUser = await getSessionUser();
  const role = sessionUser.role ?? "guest";
  const adminQueueLink = role === "admin" ? "/dashboard/admin/reviewers" : null;
  const projectLink = role === "student" ? "/dashboard/student/projects" : role === "admin" ? "/dashboard/admin/projects" : null;

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Protected Area</p>
        <h2>Dashboard</h2>
        <p>{roleMessages[role] ?? "A valid backend-issued session is required to see role-specific workflows."}</p>
      </div>
      <div className="metric-grid">
        <article className="metric">
          <h3>Security boundary</h3>
          <p>Middleware already blocks protected routes without the backend access token cookie.</p>
        </article>
        <article className="metric">
          <h3>Next build step</h3>
          <p>
            {adminQueueLink
              ? "The reviewer approval queue is now available from the admin dashboard route."
              : "Project submission, reviewer applications, and review workflows are the next domain slices."}
          </p>
        </article>
        <article className="metric">
          <h3>Domain expansion</h3>
          <p>Role-specific route groups now cover projects, sessions, reviews, and notifications, with reports still pending.</p>
        </article>
      </div>
      <div className="panel">
        <h3>Inbox</h3>
        <p>
          Open system notifications at <a href="/dashboard/notifications">/dashboard/notifications</a>.
        </p>
      </div>
      {adminQueueLink ? (
        <div className="panel">
          <h3>Admin actions</h3>
          <p>
            Open the reviewer moderation queue at <a href={adminQueueLink}>{adminQueueLink}</a>.
          </p>
          <p>
            Open the project moderation queue at <a href="/dashboard/admin/projects">/dashboard/admin/projects</a>.
          </p>
          <p>
            Manage tags, conferences, and sessions from <a href="/dashboard/admin/tags">/dashboard/admin/tags</a>, <a href="/dashboard/admin/conferences">/dashboard/admin/conferences</a>, and <a href="/dashboard/admin/sessions">/dashboard/admin/sessions</a>.
          </p>
          <p>
            Review reviewer applications at <a href="/dashboard/admin/applications">/dashboard/admin/applications</a>.
          </p>
          <p>
            Assign reviewers to approved projects at <a href="/dashboard/admin/assignments">/dashboard/admin/assignments</a>.
          </p>
        </div>
      ) : null}
      {projectLink && role === "student" ? (
        <div className="panel">
          <h3>Student actions</h3>
          <p>
            Open your project workspace at <a href={projectLink}>{projectLink}</a>.
          </p>
        </div>
      ) : null}
      {(role === "internal_reviewer" || role === "external_reviewer") ? (
        <div className="panel">
          <h3>Reviewer actions</h3>
          <p>
            Browse and apply to sessions at <a href="/dashboard/reviewer/sessions">/dashboard/reviewer/sessions</a>.
          </p>
          <p>
            Open assigned review work at <a href="/dashboard/reviewer/assignments">/dashboard/reviewer/assignments</a>.
          </p>
        </div>
      ) : null}
      <div className="panel">
        <h3>Catalog</h3>
        <p>
          Browse visible conferences and sessions at <a href="/dashboard/catalog">/dashboard/catalog</a>.
        </p>
      </div>
    </section>
  );
}
