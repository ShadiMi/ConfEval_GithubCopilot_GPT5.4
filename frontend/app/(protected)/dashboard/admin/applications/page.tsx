import { redirect } from "next/navigation";

import { ApplicationApprovalCard } from "@/components/application-approval-card";
import { getSessionUser } from "@/lib/auth";
import { getPendingReviewerApplications } from "@/lib/server-api";

export default async function AdminApplicationsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const applications = await getPendingReviewerApplications();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Queue</p>
        <h2>Reviewer applications</h2>
        <p>Approve or reject reviewer applications and assign approved reviewers to the session automatically.</p>
      </div>
      <div className="card-list">
        {applications.length === 0 ? (
          <div className="panel">
            <h3>No pending applications</h3>
            <p>The reviewer application queue is currently empty.</p>
          </div>
        ) : (
          applications.map((application) => (
            <ApplicationApprovalCard key={application.id} application={application} />
          ))
        )}
      </div>
    </section>
  );
}