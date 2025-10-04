import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useOnboarding } from '../contexts/OnboardingContext';
import { Card } from '../types/index';
import AvatarSelector from './AvatarSelector';
import ProfileGuidance from './ProfileGuidance';
import '../styles/ProfileSection.css';

interface ProfileSectionProps {
  cards?: Card[]; // For avatar display, will be used later for avatar selection
}

const ProfileSection: React.FC<ProfileSectionProps> = ({ cards = [] }) => {
  const { user, logout, updateProfile, isLoading } = useAuth();
  const { refreshOnboardingStatus } = useOnboarding();
  const [isEditingName, setIsEditingName] = useState(false);
  const [newName, setNewName] = useState(user?.name || '');
  const [nameError, setNameError] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isAvatarSelectorOpen, setIsAvatarSelectorOpen] = useState(false);

  // Find the card that matches the user's avatar
  const avatarCard = cards.find(card => card.id.toString() === user?.avatar);

  // Handle name editing
  const handleEditName = () => {
    setIsEditingName(true);
    setNewName(user?.name || '');
    setNameError('');
  };

  const handleCancelEdit = () => {
    setIsEditingName(false);
    setNewName(user?.name || '');
    setNameError('');
  };

  // Validate name according to requirements (alphanumeric and spaces only, 1-50 chars)
  const validateName = (name: string): string | null => {
    if (!name.trim()) {
      return 'Name cannot be empty';
    }
    
    if (name.length > 50) {
      return 'Name must be 50 characters or less';
    }
    
    if (!/^[a-zA-Z0-9\s]+$/.test(name)) {
      return 'Name can only contain letters, numbers, and spaces';
    }
    
    if (name.trim() !== name) {
      return 'Name cannot start or end with spaces';
    }
    
    return null;
  };

  const handleSaveName = async () => {
    const trimmedName = newName.trim();
    const validationError = validateName(trimmedName);
    
    if (validationError) {
      setNameError(validationError);
      return;
    }

    if (trimmedName === user?.name) {
      setIsEditingName(false);
      return;
    }

    setIsUpdating(true);
    try {
      await updateProfile({ name: trimmedName });
      setIsEditingName(false);
      setNameError('');
    } catch (error) {
      setNameError(error instanceof Error ? error.message : 'Failed to update name');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleAvatarSelect = async (cardId: string) => {
    setIsUpdating(true);
    try {
      await updateProfile({ avatar: cardId });
      // Close the avatar selector on success
      setIsAvatarSelectorOpen(false);
    } catch (error) {
      console.error('Failed to update avatar:', error);
      // Show user-friendly error message
      alert('Failed to update avatar. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to log out?')) {
      try {
        await logout();
      } catch (error) {
        console.error('Logout error:', error);
        // Logout should still work even if API call fails
      }
    }
  };

  if (!user) {
    return (
      <div className="profile-section">
        <div className="profile-section__error">
          <p>No user information available. Please sign in again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-section">
      <div className="profile-section__container">
        <h2 className="profile-section__title">Profile Settings</h2>
        
        {/* Profile Guidance */}
        <ProfileGuidance />
        
        {/* User Avatar */}
        <div className="profile-section__avatar">
          <div className="profile-section__avatar-container">
            {avatarCard ? (
              <img 
                src={avatarCard.image_url} 
                alt={avatarCard.name}
                className="profile-section__avatar-image"
              />
            ) : (
              <div className="profile-section__avatar-placeholder">
                <span>👤</span>
              </div>
            )}
          </div>
          <button 
            className="profile-section__avatar-button"
            onClick={() => setIsAvatarSelectorOpen(true)}
            disabled={isLoading || isUpdating}
          >
            Change Avatar
          </button>
        </div>

        {/* User Information */}
        <div className="profile-section__info">
          <div className="profile-section__field">
            <label className="profile-section__label">Email</label>
            <div className="profile-section__value profile-section__value--readonly">
              {user.email}
            </div>
          </div>

          <div className="profile-section__field">
            <label className="profile-section__label">Display Name</label>
            {isEditingName ? (
              <div className="profile-section__name-edit">
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className={`profile-section__name-input ${nameError ? 'profile-section__name-input--error' : ''}`}
                  placeholder="Enter your display name"
                  maxLength={50}
                  disabled={isUpdating}
                />
                {nameError && (
                  <div className="profile-section__error-message">
                    {nameError}
                  </div>
                )}
                <div className="profile-section__name-actions">
                  <button
                    onClick={handleSaveName}
                    className="profile-section__button profile-section__button--primary"
                    disabled={isUpdating}
                  >
                    {isUpdating ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="profile-section__button profile-section__button--secondary"
                    disabled={isUpdating}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="profile-section__name-display">
                <span className="profile-section__value">{user.name}</span>
                <button
                  onClick={handleEditName}
                  className="profile-section__edit-button"
                  disabled={isLoading}
                >
                  Edit
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Account Actions */}
        <div className="profile-section__actions">
          <button
            onClick={handleLogout}
            className="profile-section__button profile-section__button--danger"
            disabled={isLoading}
          >
            {isLoading ? 'Logging out...' : 'Log Out'}
          </button>
        </div>
      </div>

      {/* Avatar Selector Modal */}
      <AvatarSelector
        isOpen={isAvatarSelectorOpen}
        currentAvatar={user?.avatar || null}
        onSelect={handleAvatarSelect}
        onClose={() => setIsAvatarSelectorOpen(false)}
      />
    </div>
  );
};

export default ProfileSection;