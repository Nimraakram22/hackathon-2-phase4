import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { isAuthenticated } from '../services/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * Protected Route Wrapper Component
 * Redirects to login if user is not authenticated
 */
export function ProtectedRoute({ children }: ProtectedRouteProps): React.ReactElement {
  const location = useLocation();
  const authenticated = isAuthenticated();

  console.log('ProtectedRoute check:', { authenticated, path: location.pathname });

  if (!authenticated) {
    // Redirect to login with return URL
    const returnUrl = encodeURIComponent(location.pathname + location.search);
    console.log('Not authenticated, redirecting to login with returnUrl:', returnUrl);
    return <Navigate to={`/login?returnUrl=${returnUrl}`} replace />;
  }

  console.log('Authenticated, rendering protected content');
  return <>{children}</>;
}
