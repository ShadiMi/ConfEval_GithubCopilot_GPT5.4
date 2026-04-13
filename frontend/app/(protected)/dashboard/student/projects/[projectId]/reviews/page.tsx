import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getProjectCompletedReviews } from "@/lib/server-api";

export default async function ProjectReviewsPage({ params }: { params: Promise<{ projectId: string }> }) {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "student" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const { projectId } = await params;
  const projectReviews = await getProjectCompletedReviews(projectId);

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Completed Reviews</p>
        <h2>{projectReviews.project_title}</h2>
        <p><strong>Submitted reviews:</strong> {projectReviews.submitted_review_count}</p>
        <p><strong>Average score:</strong> {projectReviews.average_score ?? "Pending"}</p>
      </div>
      <div className="card-list">
        {projectReviews.reviews.length === 0 ? (
          <div className="panel">
            <h3>No completed reviews yet</h3>
            <p>Submitted reviews will appear here once reviewers finish their evaluations.</p>
          </div>
        ) : (
          projectReviews.reviews.map((review) => (
            <article className="panel" key={review.id}>
              <p className="eyebrow">Reviewer</p>
              <h3>{review.reviewer.full_name}</h3>
              <p><strong>Email:</strong> {review.reviewer.email}</p>
              <p><strong>Total score:</strong> {review.total_score ?? "Pending"}</p>
              <p><strong>Comment:</strong> {review.overall_comment ?? "No comment provided"}</p>
              <div className="card-list compact-list">
                {review.criterion_scores.map((score) => (
                  <p key={score.criteria_id}>
                    <strong>{score.criteria_name}:</strong> {score.score} / {score.max_score}
                  </p>
                ))}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}