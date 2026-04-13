import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getConferences } from "@/lib/server-api";

import { createConferenceAction } from "./actions";

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
        <form className="form" action={createConferenceAction}>
          <label>
            Name
            <input name="name" type="text" required />
          </label>
          <label>
            Description
            <textarea name="description" rows={4} />
          </label>
          <label>
            Start date
            <input name="startDate" type="date" required />
          </label>
          <label>
            End date
            <input name="endDate" type="date" required />
          </label>
          <label>
            Status
            <select name="status" defaultValue="draft">
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
          </label>
          <label>
            Building
            <select name="building" defaultValue="">
              <option value="">Use free-text location instead</option>
              <option value="ENG">Engineering Building</option>
              <option value="SCI">Science Hall</option>
              <option value="LIB">Library Annex</option>
              <option value="BUS">Business Center</option>
            </select>
          </label>
          <label>
            Floor
            <input name="floor" type="number" min="1" max="2" />
          </label>
          <label>
            Room
            <input name="room" type="number" />
          </label>
          <label>
            Free-text location
            <input name="locationText" type="text" placeholder="Optional if structured location is used" />
          </label>
          <button type="submit">Create conference</button>
        </form>
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
