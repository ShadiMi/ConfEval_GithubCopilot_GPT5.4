import { redirect } from "next/navigation";

import { ReviewerAssignmentCard } from "@/components/reviewer-assignment-card";
import { getSessionUser } from "@/lib/auth";
import { getAdminProjectAssignments } from "@/lib/server-api";

export default async function AdminAssignmentsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const projects = await getAdminProjectAssignments();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Workflow</p>
        <h2>Reviewer assignments</h2>
        <p>Assign approved session reviewers to approved projects before they can draft or submit evaluations.</p>
      </div>
      <div className="card-list">
        {projects.length === 0 ? (
          <div className="panel">
            <h3>No assignable projects</h3>
            <p>Approved projects with attached sessions will appear here.</p>
          </div>
        ) : (
          projects.map((project) => <ReviewerAssignmentCard key={project.id} project={project} />)
        )}
      </div>
    </section>
  );
}