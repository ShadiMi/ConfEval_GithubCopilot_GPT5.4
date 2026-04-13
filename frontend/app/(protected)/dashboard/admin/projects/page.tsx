import Link from "next/link";
import { redirect } from "next/navigation";

import { ProjectApprovalCard } from "@/components/project-approval-card";
import { getSessionUser } from "@/lib/auth";
import { getPendingProjects } from "@/lib/server-api";

export default async function AdminProjectsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const projects = await getPendingProjects();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Queue</p>
        <h2>Project approvals</h2>
        <p>Approve or reject pending project submissions and optionally assign poster numbers.</p>
        <p>
          <Link href="/dashboard">Back to dashboard</Link>
        </p>
      </div>
      {projects.length === 0 ? (
        <div className="panel">
          <h3>No pending projects</h3>
          <p>The project moderation queue is currently empty.</p>
        </div>
      ) : (
        <div className="card-list">
          {projects.map((project) => (
            <ProjectApprovalCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </section>
  );
}
