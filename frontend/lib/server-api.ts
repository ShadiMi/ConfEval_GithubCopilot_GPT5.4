import { cookies } from "next/headers";

import { parseBackendError } from "@/lib/api";
import { appConfig } from "@/lib/config";

export type PendingReviewer = {
  id: string;
  full_name: string;
  email: string;
  role: string;
  affiliation: string | null;
  created_at: string;
  cv_file_name: string | null;
};

export type ProjectAttachmentSummary = {
  id: string;
  kind: string;
  file_name: string;
  content_type: string;
  size_bytes: number;
};

export type ProjectSummary = {
  id: string;
  title: string;
  description: string;
  status: string;
  mentor_email: string | null;
  poster_number: string | null;
  edits_after_approval: boolean;
  created_at: string;
  owner: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
  team_members: Array<{
    id: string;
    full_name: string;
    email: string;
    role: string;
  }>;
  invitations: TeamInvitationSummary[];
  attachments: ProjectAttachmentSummary[];
};

export type TeamInvitationSummary = {
  id: string;
  email: string;
  status: string;
  token: string;
  expires_at: string;
  invited_user_id: string | null;
};

export type ProjectTeamSummary = {
  project_id: string;
  owner: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
  team_members: Array<{
    id: string;
    full_name: string;
    email: string;
    role: string;
  }>;
  pending_invitations: TeamInvitationSummary[];
};

export type TagSummary = {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type CriteriaSummary = {
  id: string;
  name: string;
  description: string | null;
  max_score: number;
  weight: number;
  display_order: number;
};

export type SessionSummary = {
  id: string;
  conference_id: string | null;
  name: string;
  description: string | null;
  start_date: string;
  end_date: string;
  status: string;
  location_label: string;
  location_text: string | null;
  max_project_capacity: number;
  reviewers_per_project: number;
  tags: TagSummary[];
  criteria: CriteriaSummary[];
};

export type ConferenceSummary = {
  id: string;
  name: string;
  description: string | null;
  start_date: string;
  end_date: string;
  status: string;
  location_label: string;
  location_text: string | null;
  location_building: string | null;
  location_floor: number | null;
  location_room: number | null;
  sessions: SessionSummary[];
};

export type ReviewerApplicationSummary = {
  id: string;
  reviewer_id: string;
  session_id: string;
  status: string;
  session_name: string;
  session_status: string;
  cover_message: string | null;
  decision_notes: string | null;
  decided_by_id: string | null;
  created_at: string;
  updated_at: string;
  reviewer: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
};

export type ReviewerAssignedProject = {
  id: string;
  title: string;
  description: string;
  status: string;
  poster_number: string | null;
  session_id: string;
  session_name: string;
  owner: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
  assigned_reviewers: Array<{
    id: string;
    full_name: string;
    email: string;
    role: string;
  }>;
  review_status: string | null;
  total_score: number | null;
  review_updated_at: string | null;
};

export type AdminProjectAssignment = {
  id: string;
  title: string;
  description: string;
  status: string;
  poster_number: string | null;
  session_id: string;
  session_name: string;
  reviewers_per_project: number;
  owner: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
  assigned_reviewers: Array<{
    id: string;
    full_name: string;
    email: string;
    role: string;
  }>;
  eligible_reviewers: Array<{
    id: string;
    full_name: string;
    email: string;
    role: string;
  }>;
  submitted_review_count: number;
  average_score: number | null;
};

export type ReviewCriterionScore = {
  criteria_id: string;
  criteria_name: string;
  description: string | null;
  max_score: number;
  weight: number;
  display_order: number;
  score: number;
};

export type ReviewSummary = {
  id: string;
  project_id: string;
  reviewer_id: string;
  session_id: string;
  status: string;
  overall_comment: string | null;
  total_score: number | null;
  created_at: string;
  updated_at: string;
  reviewer: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
  criterion_scores: ReviewCriterionScore[];
};

export type ReviewWorkspace = {
  project_id: string;
  project_title: string;
  project_description: string;
  poster_number: string | null;
  session_id: string;
  session_name: string;
  owner: {
    id: string;
    full_name: string;
    email: string;
    role: string;
  };
  assigned_reviewers: Array<{
    id: string;
    full_name: string;
    email: string;
    role: string;
  }>;
  criteria: CriteriaSummary[];
  review: ReviewSummary | null;
};

export type ProjectCompletedReviews = {
  project_id: string;
  project_title: string;
  submitted_review_count: number;
  average_score: number | null;
  reviews: ReviewSummary[];
};

export type NotificationSummary = {
  id: string;
  type: string;
  title: string;
  message: string;
  link: string | null;
  is_read: boolean;
  created_at: string;
  updated_at: string;
};

export async function backendAuthenticatedFetch(path: string, init?: RequestInit): Promise<Response> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("confeval_access_token")?.value;
  const headers = new Headers(init?.headers);

  if (!headers.has("Authorization")) {
    headers.set("Authorization", accessToken ? `Bearer ${accessToken}` : "");
  }
  if (!headers.has("Content-Type") && !(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${appConfig.backendUrl}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
}

export async function getPendingReviewers(): Promise<PendingReviewer[]> {
  const response = await backendAuthenticatedFetch("/users/pending-reviewers");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { users: PendingReviewer[] };
  return payload.users;
}

export async function getMyProjects(): Promise<ProjectSummary[]> {
  const response = await backendAuthenticatedFetch("/projects/me");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { projects: ProjectSummary[] };
  return payload.projects;
}

export async function getPendingProjects(): Promise<ProjectSummary[]> {
  const response = await backendAuthenticatedFetch("/projects/pending");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { projects: ProjectSummary[] };
  return payload.projects;
}

export async function getTags(): Promise<TagSummary[]> {
  const response = await backendAuthenticatedFetch("/tags");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { tags: TagSummary[] };
  return payload.tags;
}

export async function getConferences(): Promise<ConferenceSummary[]> {
  const response = await backendAuthenticatedFetch("/conferences");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { conferences: ConferenceSummary[] };
  return payload.conferences;
}

export async function getSessions(): Promise<SessionSummary[]> {
  const response = await backendAuthenticatedFetch("/conferences/sessions");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { sessions: SessionSummary[] };
  return payload.sessions;
}

export async function getProjectTeam(projectId: string): Promise<ProjectTeamSummary> {
  const response = await backendAuthenticatedFetch(`/projects/${projectId}/team`);
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  return (await response.json()) as ProjectTeamSummary;
}

export async function getMyPendingTeamInvitations(): Promise<TeamInvitationSummary[]> {
  const response = await backendAuthenticatedFetch("/projects/team-invitations/me");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { invitations: TeamInvitationSummary[] };
  return payload.invitations;
}

export async function getMyReviewerApplications(): Promise<ReviewerApplicationSummary[]> {
  const response = await backendAuthenticatedFetch("/reviewer-applications/me");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { applications: ReviewerApplicationSummary[] };
  return payload.applications;
}

export async function getPendingReviewerApplications(): Promise<ReviewerApplicationSummary[]> {
  const response = await backendAuthenticatedFetch("/reviewer-applications/pending");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { applications: ReviewerApplicationSummary[] };
  return payload.applications;
}

export async function getAdminProjectAssignments(): Promise<AdminProjectAssignment[]> {
  const response = await backendAuthenticatedFetch("/reviews/admin/assignments");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { projects: AdminProjectAssignment[] };
  return payload.projects;
}

export async function getReviewerAssignments(): Promise<ReviewerAssignedProject[]> {
  const response = await backendAuthenticatedFetch("/reviews/me/assignments");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { projects: ReviewerAssignedProject[] };
  return payload.projects;
}

export async function getReviewWorkspace(projectId: string): Promise<ReviewWorkspace> {
  const response = await backendAuthenticatedFetch(`/reviews/projects/${projectId}/me`);
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  return (await response.json()) as ReviewWorkspace;
}

export async function getProjectCompletedReviews(projectId: string): Promise<ProjectCompletedReviews> {
  const response = await backendAuthenticatedFetch(`/reviews/projects/${projectId}/completed`);
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  return (await response.json()) as ProjectCompletedReviews;
}

export async function getMyNotifications(): Promise<{ notifications: NotificationSummary[]; unreadCount: number }> {
  const response = await backendAuthenticatedFetch("/notifications");
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  const payload = (await response.json()) as { notifications: NotificationSummary[]; unread_count: number };
  return { notifications: payload.notifications, unreadCount: payload.unread_count };
}
