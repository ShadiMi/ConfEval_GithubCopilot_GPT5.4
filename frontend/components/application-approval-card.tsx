"use client";

import { useState } from "react";

import { approveApplicationAction, rejectApplicationAction } from "@/app/(protected)/dashboard/admin/applications/actions";
import type { ReviewerApplicationSummary } from "@/lib/server-api";

export function ApplicationApprovalCard({ application }: { application: ReviewerApplicationSummary }) {
  const [decisionNotes, setDecisionNotes] = useState("");

  return (
    <article className="panel approval-card">
      <div className="approval-card__header">
        <div>
          <p className="eyebrow">Reviewer application</p>
          <h3>{application.reviewer.full_name}</h3>
        </div>
        <span className="pill">{application.status}</span>
      </div>
      <div className="card-list">
        <p><strong>Email:</strong> {application.reviewer.email}</p>
        <p><strong>Session:</strong> {application.session_name}</p>
        <p><strong>Session status:</strong> {application.session_status}</p>
        <p><strong>Cover message:</strong> {application.cover_message ?? "No message"}</p>
      </div>
      <label className="form">
        Decision note
        <input value={decisionNotes} onChange={(event) => setDecisionNotes(event.target.value)} placeholder="Optional note" />
      </label>
      <div className="approval-card__actions">
        <form action={approveApplicationAction}>
          <input type="hidden" name="applicationId" value={application.id} />
          <input type="hidden" name="decisionNotes" value={decisionNotes} />
          <button type="submit">Approve application</button>
        </form>
        <form action={rejectApplicationAction}>
          <input type="hidden" name="applicationId" value={application.id} />
          <input type="hidden" name="decisionNotes" value={decisionNotes} />
          <button type="submit" className="button button-secondary">Reject application</button>
        </form>
      </div>
    </article>
  );
}
