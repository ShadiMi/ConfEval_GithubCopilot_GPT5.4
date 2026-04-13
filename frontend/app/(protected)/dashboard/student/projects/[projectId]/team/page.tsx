import Link from "next/link";
import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getProjectTeam } from "@/lib/server-api";

import { inviteTeamMemberAction } from "./actions";

export default async function ProjectTeamPage({ params }: { params: Promise<{ projectId: string }> }) {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "student" && sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const { projectId } = await params;
  const team = await getProjectTeam(projectId);

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Project Team</p>
        <h2>Manage team members</h2>
        <p>Invite up to two additional team members to collaborate on this project.</p>
        <p>
          <Link href="/dashboard/student/projects">Back to my projects</Link>
        </p>
      </div>
      <div className="panel">
        <form className="form" action={inviteTeamMemberAction}>
          <input type="hidden" name="projectId" value={projectId} />
          <label>
            Student email
            <input name="email" type="email" placeholder="teammate@institution.edu" required />
          </label>
          <button type="submit">Invite team member</button>
        </form>
      </div>
      <div className="card-list">
        <article className="panel">
          <p className="eyebrow">Owner</p>
          <h3>{team.owner.full_name}</h3>
          <p>{team.owner.email}</p>
        </article>
        {team.team_members.map((member) => (
          <article className="panel" key={member.id}>
            <p className="eyebrow">Team member</p>
            <h3>{member.full_name}</h3>
            <p>{member.email}</p>
          </article>
        ))}
        {team.pending_invitations.map((invitation) => (
          <article className="panel" key={invitation.id}>
            <p className="eyebrow">Pending invitation</p>
            <h3>{invitation.email}</h3>
            <p>Expires: {new Date(invitation.expires_at).toLocaleString()}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
