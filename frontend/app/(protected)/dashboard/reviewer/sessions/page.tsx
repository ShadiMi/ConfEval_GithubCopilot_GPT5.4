import { redirect } from "next/navigation";

import { SessionApplicationCard } from "@/components/session-application-card";
import { getSessionUser } from "@/lib/auth";
import { getMyReviewerApplications, getSessions } from "@/lib/server-api";

export default async function ReviewerSessionsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "internal_reviewer" && sessionUser.role !== "external_reviewer" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const [sessions, applications] = await Promise.all([getSessions(), getMyReviewerApplications()]);
  const appliedSessionIds = new Set(applications.map((application) => application.session_id));
  const availableSessions = sessions.filter((session) => !appliedSessionIds.has(session.id));

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Reviewer Sessions</p>
        <h2>Apply to sessions</h2>
        <p>Reviewers can apply to visible sessions and track the status of their applications.</p>
      </div>
      <div className="card-list">
        {availableSessions.map((session) => (
          <SessionApplicationCard key={session.id} session={session} />
        ))}
      </div>
      <div className="card-list">
        {applications.map((application) => (
          <article className="panel" key={application.id}>
            <p className="eyebrow">Application</p>
            <h3>{application.session_name}</h3>
            <p><strong>Status:</strong> {application.status}</p>
            <p><strong>Cover message:</strong> {application.cover_message ?? "No message"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}