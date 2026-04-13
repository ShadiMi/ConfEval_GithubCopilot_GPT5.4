import Link from "next/link";
import { redirect } from "next/navigation";

import { ProjectCreateForm } from "@/components/project-create-form";
import { getSessionUser } from "@/lib/auth";

export default async function NewProjectPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "student" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">New Submission</p>
        <h2>Submit a project</h2>
        <p>Projects start in the pending state and move to approved or rejected after admin review.</p>
        <p>
          <Link href="/dashboard/student/projects">Back to my projects</Link>
        </p>
      </div>
      <div className="panel">
        <ProjectCreateForm />
      </div>
      <div className="panel">
        <h3>After submission</h3>
        <p>Once the project exists, you can invite up to two additional team members from the team management page.</p>
      </div>
    </section>
  );
}
