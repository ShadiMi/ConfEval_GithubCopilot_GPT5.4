import { redirect } from "next/navigation";

import { getSessionUser } from "@/lib/auth";
import { getTags } from "@/lib/server-api";

import { createTagAction } from "./actions";

export default async function AdminTagsPage() {
  const sessionUser = await getSessionUser();
  if (sessionUser.role !== "admin") {
    redirect("/dashboard");
  }

  const tags = await getTags();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Admin Tags</p>
        <h2>Manage tags</h2>
        <form className="form" action={createTagAction}>
          <label>
            Name
            <input name="name" type="text" required />
          </label>
          <label>
            Description
            <textarea name="description" rows={4} />
          </label>
          <button type="submit">Create tag</button>
        </form>
      </div>
      <div className="card-list">
        {tags.map((tag) => (
          <article className="panel" key={tag.id}>
            <h3>{tag.name}</h3>
            <p>{tag.description ?? "No description"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
