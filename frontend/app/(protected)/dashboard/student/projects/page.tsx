import Link from "next/link";
import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getMyProjects } from "@/lib/server-api";

export default async function StudentProjectsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "student" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const projects = await getMyProjects();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Student Workspace</p>
        <h2>My projects</h2>
        <p>Create projects, attach files, and monitor the admin approval decision.</p>
        <p>
          <Link href="/dashboard/student/projects/new">Create a new project</Link>
        </p>
      </div>
      <div className="card-list">
        {projects.length === 0 ? (
          <div className="panel">
            <h3>No projects yet</h3>
            <p>Your submissions will appear here after you create them.</p>
          </div>
        ) : (
          projects.map((project) => (
            <article className="panel" key={project.id}>
              <p className="eyebrow">{project.status}</p>
              <h3>{project.title}</h3>
              <p>{project.description}</p>
              <p><strong>Poster number:</strong> {project.poster_number ?? "Not assigned"}</p>
              <p><strong>Attachments:</strong> {project.attachments.length}</p>
              <p><strong>Team members:</strong> {project.team_members.length}</p>
              <p><strong>Pending invites:</strong> {project.invitations.filter((item) => item.status === "pending").length}</p>
              <p>
                <Link href={`/dashboard/student/projects/${project.id}/team`}>Manage team</Link>
              </p>
              <p>
                <Link href={`/dashboard/student/projects/${project.id}/reviews`}>View completed reviews</Link>
              </p>
            </article>
          ))
        )}
      </div>
      <div className="panel">
        <h3>Invitation inbox</h3>
        <p>
          Review incoming invitations at <Link href="/dashboard/student/team-invitations">/dashboard/student/team-invitations</Link>.
        </p>
      </div>
    </section>
  );
}
