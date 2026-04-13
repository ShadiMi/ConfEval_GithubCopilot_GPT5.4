import { getSessionUser } from "@/lib/auth";
import { getConferences, getSessions } from "@/lib/server-api";

export default async function CatalogPage() {
  const [conferences, sessions] = await Promise.all([getConferences(), getSessions()]);
  const sessionUser = await getSessionUser();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Catalog</p>
        <h2>Visible conferences and sessions</h2>
        <p>
          {sessionUser.role === "admin"
            ? "Admin view includes all conferences and sessions."
            : "Non-admin view includes active conferences and upcoming or active sessions only."}
        </p>
      </div>
      <div className="card-list">
        {conferences.map((conference) => (
          <article className="panel" key={conference.id}>
            <p className="eyebrow">Conference</p>
            <h3>{conference.name}</h3>
            <p>{conference.location_label}</p>
            <p>{conference.description ?? "No description"}</p>
          </article>
        ))}
      </div>
      <div className="card-list">
        {sessions.map((session) => (
          <article className="panel" key={session.id}>
            <p className="eyebrow">Session</p>
            <h3>{session.name}</h3>
            <p>{session.location_label}</p>
            <p>{session.description ?? "No description"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
