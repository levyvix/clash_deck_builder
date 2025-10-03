import React, { useEffect } from 'react';
import { Notification as NotificationType } from '../types';
import '../styles/Notification.css';

interface NotificationProps {
  notifications: NotificationType[];
  onDismiss: (id: string) => void;
}

const Notification: React.FC<NotificationProps> = ({ notifications, onDismiss }) => {
  useEffect(() => {
    // Auto-dismiss notifications after 3 seconds
    notifications.forEach((notification) => {
      const timer = setTimeout(() => {
        onDismiss(notification.id);
      }, 3000);

      return () => clearTimeout(timer);
    });
  }, [notifications, onDismiss]);

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification notification--${notification.type}`}
          role="alert"
          aria-live="polite"
        >
          <span className="notification__message">{notification.message}</span>
          <button
            className="notification__dismiss"
            onClick={() => onDismiss(notification.id)}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
};

export default Notification;
