const highlights = [
  {
    title: "Reviewer approval gates",
    description: "Manual admin approval is treated as a first-class security boundary before reviewer login.",
  },
  {
    title: "Structured evaluations",
    description: "Sessions carry weighted criteria, per-project assignments, and auditable score aggregation.",
  },
  {
    title: "Institution-grade control",
    description: "Admins govern conferences, sessions, users, tags, assignments, reports, and notifications.",
  },
];

export default function HomePage() {
  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Security-First Academic Workflow</p>
        <h2>Manage conferences, projects, reviewer approval, and criteria-based evaluation in one system.</h2>
        <p>
          ConfEval is being built as a full-stack platform for academic institutions running poster and conference review programs.
        </p>
      </div>
      <div className="hero-grid">
        {highlights.map((item) => (
          <article className="metric" key={item.title}>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
