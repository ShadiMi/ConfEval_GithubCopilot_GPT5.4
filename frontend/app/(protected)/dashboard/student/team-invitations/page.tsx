import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getMyPendingTeamInvitations } from "@/lib/server-api";

import { acceptInvitationAction, declineInvitationAction } from "./actions";

export default async function TeamInvitationsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "student" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const invitations = await getMyPendingTeamInvitations();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Team Invitations</p>
        <h2>Pending invitations</h2>
        <p>Accept or decline invitations sent to your student email address.</p>
      </div>
      <div className="card-list">
        {invitations.length === 0 ? (
          <div className="panel">
            <h3>No pending invitations</h3>
            <p>You do not have any team invitations waiting for a response.</p>
          </div>
        ) : (
          invitations.map((invitation) => (
            <article className="panel approval-card" key={invitation.id}>
              <div>
                <p className="eyebrow">Invitation</p>
                <h3>{invitation.email}</h3>
                <p>Expires: {new Date(invitation.expires_at).toLocaleString()}</p>
              </div>
              <div className="approval-card__actions">
                <form action={acceptInvitationAction}>
                  <input type="hidden" name="token" value={invitation.token} />
                  <button type="submit">Accept</button>
                </form>
                <form action={declineInvitationAction}>
                  <input type="hidden" name="token" value={invitation.token} />
                  <button type="submit" className="button button-secondary">Decline</button>
                </form>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
