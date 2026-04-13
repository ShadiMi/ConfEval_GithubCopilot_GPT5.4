"use client";

import { useState } from "react";

import { approveReviewerAction, rejectReviewerAction } from "@/app/(protected)/dashboard/admin/reviewers/actions";
import type { PendingReviewer } from "@/lib/server-api";

export function ReviewerApprovalCard({ reviewer }: { reviewer: PendingReviewer }) {
  const [reason, setReason] = useState("");

  return (
    <article className="panel approval-card">
      <div className="approval-card__header">
        <div>
          <p className="eyebrow">Pending reviewer</p>
          <h3>{reviewer.full_name}</h3>
        </div>
        <span className="pill">{reviewer.role.replaceAll("_", " ")}</span>
      </div>
      <div className="card-list">
        <p><strong>Email:</strong> {reviewer.email}</p>
        <p><strong>Affiliation:</strong> {reviewer.affiliation ?? "Not provided"}</p>
        <p><strong>Registered:</strong> {new Date(reviewer.created_at).toLocaleString()}</p>
        <p>
          <strong>CV:</strong>{" "}
          {reviewer.cv_file_name ? (
            <a href={`/api/reviewers/${reviewer.id}/cv`} target="_blank" rel="noreferrer">
              {reviewer.cv_file_name}
            </a>
          ) : (
            "Not uploaded"
          )}
        </p>
      </div>
      <label className="form">
        Decision note
        <input value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Optional decision note" />
      </label>
      <div className="approval-card__actions">
        <form action={approveReviewerAction}>
          <input type="hidden" name="userId" value={reviewer.id} />
          <input type="hidden" name="reason" value={reason} />
          <button type="submit">Approve reviewer</button>
        </form>
        <form action={rejectReviewerAction}>
          <input type="hidden" name="userId" value={reviewer.id} />
          <input type="hidden" name="reason" value={reason} />
          <button type="submit" className="button button-secondary">Reject reviewer</button>
        </form>
      </div>
    </article>
  );
}
