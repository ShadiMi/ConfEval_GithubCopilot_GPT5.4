"use client";

import Link from "next/link";
import { useState } from "react";

import { approveProjectAction, rejectProjectAction } from "@/app/(protected)/dashboard/admin/projects/actions";
import type { ProjectSummary } from "@/lib/server-api";

export function ProjectApprovalCard({ project }: { project: ProjectSummary }) {
  const [reason, setReason] = useState("");
  const [posterNumber, setPosterNumber] = useState(project.poster_number ?? "");

  return (
    <article className="panel approval-card">
      <div className="approval-card__header">
        <div>
          <p className="eyebrow">Pending project</p>
          <h3>{project.title}</h3>
        </div>
        <span className="pill">{project.status}</span>
      </div>
      <div className="card-list">
        <p><strong>Owner:</strong> {project.owner.full_name} ({project.owner.email})</p>
        <p><strong>Mentor:</strong> {project.mentor_email ?? "Not provided"}</p>
        <p><strong>Description:</strong> {project.description}</p>
        <p><strong>Submitted:</strong> {new Date(project.created_at).toLocaleString()}</p>
        <div>
          <strong>Attachments:</strong>
          <div className="card-list compact-list">
            {project.attachments.length === 0 ? (
              <p>No attachments uploaded.</p>
            ) : (
              project.attachments.map((attachment) => (
                <p key={attachment.id}>
                  <Link href={`/api/projects/${project.id}/attachments/${attachment.kind}`} target="_blank">
                    {attachment.file_name}
                  </Link>
                </p>
              ))
            )}
          </div>
        </div>
      </div>
      <label className="form">
        Poster number
        <input value={posterNumber} onChange={(event) => setPosterNumber(event.target.value)} placeholder="Optional on approval" />
      </label>
      <label className="form">
        Decision note
        <input value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Optional reason" />
      </label>
      <div className="approval-card__actions">
        <form action={approveProjectAction}>
          <input type="hidden" name="projectId" value={project.id} />
          <input type="hidden" name="posterNumber" value={posterNumber} />
          <input type="hidden" name="reason" value={reason} />
          <button type="submit">Approve project</button>
        </form>
        <form action={rejectProjectAction}>
          <input type="hidden" name="projectId" value={project.id} />
          <input type="hidden" name="reason" value={reason} />
          <button type="submit" className="button button-secondary">Reject project</button>
        </form>
      </div>
    </article>
  );
}
