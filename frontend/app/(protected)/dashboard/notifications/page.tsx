import Link from "next/link";

import { markAllNotificationsReadAction, markNotificationReadAction } from "@/app/(protected)/dashboard/notifications/actions";
import { getMyNotifications } from "@/lib/server-api";

export default async function NotificationsPage() {
  const { notifications, unreadCount } = await getMyNotifications();

  return (
    <section className="hero">
      <div className="panel">
        <p className="eyebrow">Inbox</p>
        <h2>Notifications</h2>
        <p>Unread: {unreadCount}</p>
        <form action={markAllNotificationsReadAction}>
          <button type="submit" className="button button-secondary">Mark all as read</button>
        </form>
      </div>
      <div className="card-list">
        {notifications.length === 0 ? (
          <div className="panel">
            <h3>No notifications yet</h3>
            <p>Approval decisions, assignments, and review events will appear here.</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <article className="panel approval-card" key={notification.id}>
              <div className="approval-card__header">
                <div>
                  <p className="eyebrow">{notification.type}</p>
                  <h3>{notification.title}</h3>
                </div>
                <span className="pill">{notification.is_read ? "read" : "unread"}</span>
              </div>
              <div className="card-list compact-list">
                <p>{notification.message}</p>
                <p><strong>Received:</strong> {new Date(notification.created_at).toLocaleString()}</p>
                {notification.link ? (
                  <p>
                    <Link href={notification.link}>Open related page</Link>
                  </p>
                ) : null}
              </div>
              {!notification.is_read ? (
                <form action={markNotificationReadAction}>
                  <input type="hidden" name="notificationId" value={notification.id} />
                  <button type="submit">Mark as read</button>
                </form>
              ) : null}
            </article>
          ))
        )}
      </div>
    </section>
  );
}