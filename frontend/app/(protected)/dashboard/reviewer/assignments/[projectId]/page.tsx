import { redirect } from "next/navigation";

import { saveReviewAction } from "@/app/(protected)/dashboard/reviewer/assignments/[projectId]/actions";
import { getSessionUser } from "@/lib/auth";
import { getReviewWorkspace } from "@/lib/server-api";

export default async function ReviewerProjectReviewPage({ params }: { params: Promise<{ projectId: string }> }) {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "internal_reviewer" && sessionUser.role !== "external_reviewer" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const { projectId } = await params;
  const workspace = await getReviewWorkspace(projectId);
  const currentScores = new Map(workspace.review?.criterion_scores.map((score) => [score.criteria_id, score.score]) ?? []);

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Reviewer Workspace</p>
        <h2>{workspace.project_title}</h2>
        <p>{workspace.project_description}</p>
        <p><strong>Session:</strong> {workspace.session_name}</p>
        <p><strong>Owner:</strong> {workspace.owner.full_name} ({workspace.owner.email})</p>
        <p><strong>Status:</strong> {workspace.review?.status ?? "not started"}</p>
      </div>
      <form action={saveReviewAction} className="panel form">
        <input type="hidden" name="projectId" value={workspace.project_id} />
        {workspace.criteria.map((criteria) => (
          <label key={criteria.id}>
            {criteria.name} ({criteria.weight}x, max {criteria.max_score})
            <input
              type="number"
              name={`score:${criteria.id}`}
              min={0}
              max={criteria.max_score}
              step="0.01"
              defaultValue={currentScores.get(criteria.id) ?? ""}
            />
          </label>
        ))}
        <label>
          Overall comment
          <textarea name="overallComment" defaultValue={workspace.review?.overall_comment ?? ""} />
        </label>
        <div className="approval-card__actions">
          <button type="submit" name="intent" value="draft" className="button button-secondary">Save draft</button>
          <button type="submit" name="intent" value="submit">Submit review</button>
        </div>
      </form>
    </section>
  );
}