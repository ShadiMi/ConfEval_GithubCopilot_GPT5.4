import { redirect } from "next/navigation";

import { ConferenceCreateForm } from "@/components/conference-create-form";
import { getSessionUser } from "@/lib/auth";
import { getConferences } from "@/lib/server-api";

export default async function AdminConferencesPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const conferences = await getConferences();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Conferences</p>
        <h2>Manage conferences</h2>
        <ConferenceCreateForm />
      </div>
      <div className="card-list">
        {conferences.map((conference) => (
          <article className="panel" key={conference.id}>
            <p className="eyebrow">{conference.status}</p>
            <h3>{conference.name}</h3>
            <p>{conference.location_label}</p>
            <p>{conference.description ?? "No description"}</p>
            <p><strong>Sessions:</strong> {conference.sessions.length}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
