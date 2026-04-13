import { saveProjectAssignmentsAction } from "@/app/(protected)/dashboard/admin/assignments/actions";
import type { AdminProjectAssignment } from "@/lib/server-api";

export function ReviewerAssignmentCard({ project }: { project: AdminProjectAssignment }) {
  const assignedReviewerIds = new Set(project.assigned_reviewers.map((reviewer) => reviewer.id));

  return (
    <article className="panel approval-card">
      <div className="approval-card__header">
        <div>
          <p className="eyebrow">Reviewer assignment</p>
          <h3>{project.title}</h3>
        </div>
        <span className="pill">{project.submitted_review_count}/{project.reviewers_per_project} submitted</span>
      </div>
      <div className="card-list compact-list">
        <p><strong>Owner:</strong> {project.owner.full_name} ({project.owner.email})</p>
        <p><strong>Session:</strong> {project.session_name}</p>
        <p><strong>Poster:</strong> {project.poster_number ?? "Not assigned"}</p>
        <p><strong>Description:</strong> {project.description}</p>
        <p><strong>Average score:</strong> {project.average_score ?? "No submitted reviews"}</p>
      </div>
      <form action={saveProjectAssignmentsAction} className="form">
        <input type="hidden" name="projectId" value={project.id} />
        <fieldset className="form-fieldset">
          <legend>Select up to {project.reviewers_per_project} reviewers</legend>
          <div className="checkbox-grid">
            {project.eligible_reviewers.length === 0 ? (
              <p>No approved reviewers are attached to this session yet.</p>
            ) : (
              project.eligible_reviewers.map((reviewer) => (
                <label className="checkbox-row" key={reviewer.id}>
                  <input type="checkbox" name="reviewerId" value={reviewer.id} defaultChecked={assignedReviewerIds.has(reviewer.id)} />
                  <span>{reviewer.full_name} ({reviewer.email})</span>
                </label>
              ))
            )}
          </div>
        </fieldset>
        <button type="submit">Save assignments</button>
      </form>
    </article>
  );
}