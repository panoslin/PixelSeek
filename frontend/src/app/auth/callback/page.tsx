"use client";

import { useEffect, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Message } from 'primereact/message';
import { useAuth } from '@/context/AuthContext';

export default function OAuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(true);
  
  // Use a ref to track if auth has been processed to prevent multiple executions
  const authProcessedRef = useRef(false);

  useEffect(() => {
    // Store cleanup functions
    let isActive = true;
    let redirectTimer: NodeJS.Timeout;
    
    const handleCallback = async () => {
      // Skip if already processed
      if (authProcessedRef.current) {
        return;
      }
      
      // Mark as processed
      authProcessedRef.current = true;
      
      try {
        // Check for error in params
        if (searchParams.has('error')) {
          throw new Error(searchParams.get('error') || 'Authentication failed');
        }

        // Parse tokens from the URL
        const tokensParam = searchParams.get('tokens');
        if (!tokensParam) {
          throw new Error('No authentication tokens received');
        }

        // Parse the token data
        const tokens = JSON.parse(decodeURIComponent(tokensParam));
        
        if (!tokens.access) {
          throw new Error('Invalid token data received');
        }

        // Use AuthContext login method to handle authentication
        if (isActive) {
          await login({
            access: tokens.access,
            refresh: tokens.refresh || ''
          });

          // Clean up any OAuth state
          localStorage.removeItem('oauth_provider');
          localStorage.removeItem('oauth_state');

          // Redirect to home page after a short delay
          redirectTimer = setTimeout(() => {
            if (isActive) {
              router.push('/home');
            }
          }, 1000);
        }
      } catch (err) {
        if (isActive) {
          console.error('Authentication callback error:', err);
          setError(err instanceof Error ? err.message : 'Authentication failed');
          setProcessing(false);
          
          // Redirect to login after showing error
          redirectTimer = setTimeout(() => {
            if (isActive) {
              router.push('/auth/login');
            }
          }, 3000);
        }
      }
    };

    handleCallback();
    
    // Cleanup function
    return () => {
      isActive = false;
      if (redirectTimer) {
        clearTimeout(redirectTimer);
      }
    };
  }, []); // Empty dependency array since we use ref to manage execution

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#121212] p-4">
      <div className="w-full max-w-md bg-[#1a1a1a] rounded-lg shadow-lg p-6 text-center">
        {processing && !error ? (
          <>
            <h1 className="text-2xl font-bold text-white mb-4">Completing Authentication</h1>
            <div className="flex justify-center mb-4">
              <ProgressSpinner 
                style={{ width: '50px', height: '50px' }} 
                strokeWidth="4" 
                fill="#1a1a1a" 
                animationDuration=".5s" 
              />
            </div>
            <p className="text-gray-400">Please wait while we complete your sign-in process...</p>
          </>
        ) : error ? (
          <>
            <Message 
              severity="error" 
              text={error} 
              className="w-full mb-4" 
              style={{ justifyContent: 'center' }}
            />
            <p className="text-gray-400 mt-4">Redirecting to login page...</p>
          </>
        ) : null}
      </div>
    </div>
  );
} 