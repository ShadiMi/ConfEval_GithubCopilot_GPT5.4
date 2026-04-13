import Link from "next/link";
import { redirect } from "next/navigation";

import { ReviewerApprovalCard } from "@/components/reviewer-approval-card";
import { getSessionUser } from "@/lib/auth";
import { getPendingReviewers } from "@/lib/server-api";

export default async function AdminReviewerApprovalsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const reviewers = await getPendingReviewers();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Queue</p>
        <h2>Reviewer approvals</h2>
        <p>Approve or reject reviewer accounts before they can sign in and access session-review workflows.</p>
        <p>
          <Link href="/dashboard">Back to dashboard</Link>
        </p>
      </div>
      {reviewers.length === 0 ? (
        <div className="panel">
          <h3>No pending reviewers</h3>
          <p>The moderation queue is currently empty.</p>
        </div>
      ) : (
        <div className="card-list">
          {reviewers.map((reviewer) => (
            <ReviewerApprovalCard key={reviewer.id} reviewer={reviewer} />
          ))}
        </div>
      )}
    </section>
  );
}
