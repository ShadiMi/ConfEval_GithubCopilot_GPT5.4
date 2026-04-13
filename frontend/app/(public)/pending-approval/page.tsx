export default function PendingApprovalPage() {
  return (
    <section className="panel">
      <p className="eyebrow">Reviewer Approval</p>
      <h2>Account pending approval</h2>
      <p>
        Reviewer accounts cannot sign in until an administrator approves them. Once approved, you can return to the login page and access your reviewer dashboard.
      </p>
      <div className="metric-grid">
        <article className="metric">
          <h3>What admins review</h3>
          <p>Profile details, affiliation, and eventually uploaded CV materials for reviewer verification.</p>
        </article>
        <article className="metric">
          <h3>What happens next</h3>
          <p>Admins receive an in-app notification and can approve or reject the account from the review queue.</p>
        </article>
        <article className="metric">
          <h3>When to return</h3>
          <p>After approval, use the same credentials on the login page to continue into assigned sessions and reviews.</p>
        </article>
      </div>
    </section>
  );
}
