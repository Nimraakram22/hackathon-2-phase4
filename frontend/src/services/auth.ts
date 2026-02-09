/**
 * Authentication Service
 * Session management with JWT tokens
 * Implements 24h default, 30d with "Remember Me" (US3)
 */

export interface Session {
  token: string;
  userId: string;
  expiresAt: number; // Unix timestamp
}

export interface SetSessionOptions {
  token: string;
  userId: string;
  expiresInDays: number;
}

const SESSION_KEY = 'auth_session';

/**
 * Set session in localStorage with expiration
 */
export function setSession(options: SetSessionOptions): void {
  const { token, userId, expiresInDays } = options;

  const expiresAt = Date.now() + (expiresInDays * 24 * 60 * 60 * 1000);

  const session: Session = {
    token,
    userId,
    expiresAt,
  };

  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

/**
 * Get current session from localStorage
 * Returns null if session is expired or doesn't exist
 */
export function getSession(): Session | null {
  try {
    const sessionStr = localStorage.getItem(SESSION_KEY);
    if (!sessionStr) {
      return null;
    }

    const session: Session = JSON.parse(sessionStr);

    // Check if session is expired
    if (Date.now() > session.expiresAt) {
      clearSession();
      return null;
    }

    return session;
  } catch (error) {
    console.error('Error reading session:', error);
    clearSession();
    return null;
  }
}

/**
 * Clear session from localStorage
 */
export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getSession() !== null;
}

/**
 * Get authentication token
 */
export function getAuthToken(): string | null {
  const session = getSession();
  return session?.token || null;
}

/**
 * Get current user ID
 */
export function getUserId(): string | null {
  const session = getSession();
  return session?.userId || null;
}

/**
 * Refresh session expiration (extend by original duration)
 * Useful for keeping active users logged in
 */
export function refreshSession(): boolean {
  const session = getSession();
  if (!session) {
    return false;
  }

  // Calculate original duration
  const originalDuration = session.expiresAt - Date.now();
  const daysRemaining = Math.ceil(originalDuration / (24 * 60 * 60 * 1000));

  // Extend by same duration
  setSession({
    token: session.token,
    userId: session.userId,
    expiresInDays: daysRemaining,
  });

  return true;
}
