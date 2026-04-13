import Link from "next/link";
import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getReviewerAssignments } from "@/lib/server-api";

export default async function ReviewerAssignmentsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "internal_reviewer" && sessionUser.role !== "external_reviewer" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const projects = await getReviewerAssignments();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Reviewer Workflow</p>
        <h2>Assigned projects</h2>
        <p>Open each assigned project to draft or submit the review against the session criteria.</p>
      </div>
      <div className="card-list">
        {projects.length === 0 ? (
          <div className="panel">
            <h3>No assignments yet</h3>
            <p>Projects will appear here after an admin assigns you to them.</p>
          </div>
        ) : (
          projects.map((project) => (
            <article className="panel" key={project.id}>
              <p className="eyebrow">{project.session_name}</p>
              <h3>{project.title}</h3>
              <p>{project.description}</p>
              <p><strong>Student owner:</strong> {project.owner.full_name}</p>
              <p><strong>Review status:</strong> {project.review_status ?? "Not started"}</p>
              <p><strong>Total score:</strong> {project.total_score ?? "Pending"}</p>
              <p>
                <Link href={`/dashboard/reviewer/assignments/${project.id}`}>Open review workspace</Link>
              </p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}