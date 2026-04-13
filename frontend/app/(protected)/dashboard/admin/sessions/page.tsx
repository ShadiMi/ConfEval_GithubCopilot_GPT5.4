import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getConferences, getSessions, getTags } from "@/lib/server-api";

import { createSessionAction } from "./actions";

export default async function AdminSessionsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const [conferences, sessions, tags] = await Promise.all([getConferences(), getSessions(), getTags()]);

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Sessions</p>
        <h2>Manage sessions</h2>
        <form className="form" action={createSessionAction}>
          <label>
            Conference
            <select name="conferenceId" defaultValue="">
              <option value="">Standalone session</option>
              {conferences.map((conference) => (
                <option key={conference.id} value={conference.id}>{conference.name}</option>
              ))}
            </select>
          </label>
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
            <select name="status" defaultValue="upcoming">
              <option value="upcoming">Upcoming</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </label>
          <label>
            Location
            <input name="locationText" type="text" required />
          </label>
          <label>
            Max project capacity
            <input name="maxProjectCapacity" type="number" min="1" defaultValue="10" required />
          </label>
          <label>
            Reviewers per project
            <input name="reviewersPerProject" type="number" min="1" max="10" defaultValue="2" required />
          </label>
          <label>
            Criteria name
            <input name="criteriaName" type="text" required />
          </label>
          <label>
            Criteria description
            <input name="criteriaDescription" type="text" />
          </label>
          <label>
            Criteria max score
            <input name="criteriaMaxScore" type="number" min="1" max="100" defaultValue="100" required />
          </label>
          <label>
            Criteria weight
            <input name="criteriaWeight" type="number" min="0.1" max="10" step="0.1" defaultValue="1" required />
          </label>
          <fieldset className="form-fieldset">
            <legend>Tags</legend>
            <div className="checkbox-grid">
              {tags.map((tag) => (
                <label key={tag.id} className="checkbox-row">
                  <input type="checkbox" name="tagIds" value={tag.id} />
                  <span>{tag.name}</span>
                </label>
              ))}
            </div>
          </fieldset>
          <button type="submit">Create session</button>
        </form>
      </div>
      <div className="card-list">
        {sessions.map((session) => (
          <article className="panel" key={session.id}>
            <p className="eyebrow">{session.status}</p>
            <h3>{session.name}</h3>
            <p>{session.location_label}</p>
            <p><strong>Criteria:</strong> {session.criteria.length}</p>
            <p><strong>Tags:</strong> {session.tags.map((tag) => tag.name).join(", ") || "None"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
