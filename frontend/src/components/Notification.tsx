import React, { useEffect, useState } from 'react';
import { Notification as NotificationType } from '../types';
import '../styles/Notification.css';

interface NotificationProps {
  notifications: NotificationType[];
  onDismiss: (id: string) => void;
}

interface NotificationState {
  id: string;
  state: 'entering' | 'visible' | 'leaving';
}

const Notification: React.FC<NotificationProps> = ({ notifications, onDismiss }) => {
  const [notificationStates, setNotificationStates] = useState<Map<string, NotificationState>>(new Map());

  // Track notification lifecycle states
  useEffect(() => {
    setNotificationStates((prevStates) => {
      const newStates = new Map(prevStates);
      
      // Add new notifications in entering state
      notifications.forEach((notification) => {
        if (!newStates.has(notification.id)) {
          newStates.set(notification.id, { id: notification.id, state: 'entering' });
          
          // Transition to visible after animation completes
          setTimeout(() => {
            setNotificationStates((prev) => {
              const updated = new Map(prev);
              const current = updated.get(notification.id);
              if (current && current.state === 'entering') {
                updated.set(notification.id, { id: notification.id, state: 'visible' });
              }
              return updated;
            });
          }, 250);
        }
      });

      // Remove states for notifications that no longer exist
      const currentIds = new Set(notifications.map(n => n.id));
      Array.from(newStates.keys()).forEach((id) => {
        if (!currentIds.has(id)) {
          newStates.delete(id);
        }
      });

      // Only update if there are actual changes
      if (newStates.size !== prevStates.size || 
          Array.from(newStates.keys()).some(id => !prevStates.has(id))) {
        return newStates;
      }
      
      return prevStates;
    });
  }, [notifications]);

  // Auto-dismiss notifications after 3 seconds
  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];
    
    notifications.forEach((notification) => {
      const timer = setTimeout(() => {
        onDismiss(notification.id);
      }, 3000);
      timers.push(timer);
    });

    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [notifications, onDismiss]);

  if (notifications.length === 0) {
    return null;
  }

  const getAnimationClass = (id: string): string => {
    const state = notificationStates.get(id);
    if (!state) return 'notification--entering';
    
    switch (state.state) {
      case 'entering':
        return 'notification--entering';
      case 'leaving':
        return 'notification--leaving';
      default:
        return '';
    }
  };

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification notification--${notification.type} ${getAnimationClass(notification.id)}`}
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
