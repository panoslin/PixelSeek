'use client';

import React, { ReactNode } from 'react';
import { AuthProvider } from './context/AuthContext';
import { PrimeReactProvider } from 'primereact/api';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <PrimeReactProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </PrimeReactProvider>
  );
}

export default Providers; 