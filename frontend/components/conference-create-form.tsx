"use client";

import { useActionState } from "react";

import { createConferenceAction, type ConferenceActionState } from "@/app/(protected)/dashboard/admin/conferences/actions";

const initialState: ConferenceActionState = {
  error: null,
};

export function ConferenceCreateForm() {
  const [state, action, pending] = useActionState(createConferenceAction, initialState);

  return (
    <form className="form" action={action}>
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
      {state.error ? <p className="form-error">{state.error}</p> : null}
      <button type="submit" disabled={pending}>
        {pending ? "Creating conference..." : "Create conference"}
      </button>
    </form>
  );
}