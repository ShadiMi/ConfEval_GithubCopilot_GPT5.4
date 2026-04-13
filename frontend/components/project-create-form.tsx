"use client";

import { useActionState } from "react";

import { createProjectAction, type ProjectCreateState } from "@/app/(protected)/dashboard/student/projects/new/actions";

const initialState: ProjectCreateState = {
  error: null,
};

export function ProjectCreateForm() {
  const [state, action, pending] = useActionState(createProjectAction, initialState);

  return (
    <form className="form" action={action} encType="multipart/form-data">
      <label>
        Title
        <input name="title" type="text" placeholder="Project title" required />
      </label>
      <label>
        Description
        <textarea name="description" placeholder="Project abstract or summary" rows={6} required />
      </label>
      <label>
        Mentor email
        <input name="mentorEmail" type="email" placeholder="Optional mentor email" />
      </label>
      <label>
        Session ID
        <input name="sessionId" type="text" placeholder="Optional session UUID" />
      </label>
      <label>
        Paper
        <input name="paperFile" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" />
      </label>
      <label>
        Slides
        <input name="slidesFile" type="file" accept=".pdf,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.presentationml.presentation" />
      </label>
      <label>
        Additional material
        <input name="additionalFile" type="file" accept=".pdf,.docx,.xlsx,.zip,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/zip" />
      </label>
      {state.error ? <p className="form-error">{state.error}</p> : null}
      <button type="submit" disabled={pending}>
        {pending ? "Submitting project..." : "Submit project"}
      </button>
    </form>
  );
}
