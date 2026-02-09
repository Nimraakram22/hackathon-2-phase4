/**
 * Authentication Middleware for React Router v7
 * Checks if user is authenticated before allowing access to protected routes
 */

interface AuthMiddlewareContext {
  request: Request;
  context: Record<string, unknown>;
}

interface User {
  id: number;
  email: string;
}

/**
 * Get user session from localStorage
 */
function getSession(): { userId: number; token: string } | null {
  try {
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');

    if (!token || !userId) {
      return null;
    }

    return {
      userId: parseInt(userId, 10),
      token,
    };
  } catch (error) {
    console.error('Error reading session:', error);
    return null;
  }
}

/**
 * Authentication middleware
 * Redirects to /login if user is not authenticated
 */
export async function authMiddleware(
  { request, context }: AuthMiddlewareContext,
  next: () => Promise<Response>
): Promise<Response> {
  const session = getSession();

  if (!session) {
    // Redirect to login with return URL
    const url = new URL(request.url);
    const returnUrl = encodeURIComponent(url.pathname + url.search);
    return Response.redirect(`/login?returnUrl=${returnUrl}`, 302);
  }

  // Add user to context for downstream loaders
  context.user = {
    id: session.userId,
    token: session.token,
  };

  // Continue to the route
  return next();
}

/**
 * Check if user is authenticated (for use in components)
 */
export function isAuthenticated(): boolean {
  return getSession() !== null;
}

/**
 * Get current user from session
 */
export function getCurrentUser(): User | null {
  const session = getSession();
  if (!session) {
    return null;
  }

  // In a real app, you might want to fetch user details from API
  // For now, return basic info from session
  return {
    id: session.userId,
    email: '', // Would be fetched from API or stored in session
  };
}

/**
 * Clear session (logout)
 */
export function clearSession(): void {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('refresh_token');
}

/**
 * Set session (login)
 */
export function setSession(userId: number, token: string, refreshToken?: string): void {
  localStorage.setItem('auth_token', token);
  localStorage.setItem('user_id', userId.toString());
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken);
  }
}
