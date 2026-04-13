"use client";

import { useState } from "react";

import { applyToSessionAction } from "@/app/(protected)/dashboard/reviewer/sessions/actions";
import type { SessionSummary } from "@/lib/server-api";

export function SessionApplicationCard({ session }: { session: SessionSummary }) {
  const [coverMessage, setCoverMessage] = useState("");

  return (
    <article className="panel approval-card">
      <div className="approval-card__header">
        <div>
          <p className="eyebrow">Session</p>
          <h3>{session.name}</h3>
        </div>
        <span className="pill">{session.status}</span>
      </div>
      <div className="card-list">
        <p>{session.description ?? "No description"}</p>
        <p><strong>Location:</strong> {session.location_label}</p>
        <p><strong>Tags:</strong> {session.tags.map((tag) => tag.name).join(", ") || "None"}</p>
      </div>
      <form className="form" action={applyToSessionAction}>
        <input type="hidden" name="sessionId" value={session.id} />
        <label>
          Cover message
          <textarea name="coverMessage" value={coverMessage} onChange={(event) => setCoverMessage(event.target.value)} rows={4} />
        </label>
        <button type="submit">Apply to session</button>
      </form>
    </article>
  );
}
