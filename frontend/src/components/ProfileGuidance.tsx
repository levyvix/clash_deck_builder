import React from 'react';
import { useOnboarding } from '../contexts/OnboardingContext';
import { useAuth } from '../contexts/AuthContext';
import '../styles/ProfileGuidance.css';

const ProfileGuidance: React.FC = () => {
  const { user } = useAuth();
  const { needsProfileSetup, profileCompletion, showOnboardingModal } = useOnboarding();

  if (!user || (!needsProfileSetup && profileCompletion?.isComplete)) {
    return null;
  }

  const incompleteTasks = [];
  
  if (profileCompletion?.items) {
    if (!profileCompletion.items.has_avatar) {
      incompleteTasks.push({
        id: 'avatar',
        title: 'Choose Your Avatar',
        description: 'Select a Clash Royale card as your profile avatar',
        icon: '🎭'
      });
    }
    
    if (!profileCompletion.items.has_custom_name) {
      incompleteTasks.push({
        id: 'name',
        title: 'Customize Your Name',
        description: 'Update your display name to personalize your profile',
        icon: '✏️'
      });
    }
  }

  if (incompleteTasks.length === 0) {
    return null;
  }

  return (
    <div className="profile-guidance">
      <div className="profile-guidance__header">
        <h3 className="profile-guidance__title">
          Complete Your Profile
        </h3>
        <div className="profile-guidance__progress">
          <div className="profile-guidance__progress-bar">
            <div 
              className="profile-guidance__progress-fill"
              style={{ width: `${profileCompletion?.percentage || 0}%` }}
            />
          </div>
          <span className="profile-guidance__progress-text">
            {profileCompletion?.percentage || 0}% Complete
          </span>
        </div>
      </div>

      <div className="profile-guidance__tasks">
        {incompleteTasks.map((task) => (
          <div key={task.id} className="profile-guidance__task">
            <div className="profile-guidance__task-icon">
              {task.icon}
            </div>
            <div className="profile-guidance__task-content">
              <h4 className="profile-guidance__task-title">
                {task.title}
              </h4>
              <p className="profile-guidance__task-description">
                {task.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="profile-guidance__actions">
        <button
          className="profile-guidance__help-button"
          onClick={showOnboardingModal}
        >
          Show Setup Guide
        </button>
      </div>
    </div>
  );
};

export default ProfileGuidance;