import './globals.css';
import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from '@/providers';

// PrimeReact imports
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/lara-dark-indigo/theme.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

import TopBar from '@/components/TopBar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'PixelSeek - Find the perfect image',
  description: 'Advanced AI-powered image search platform',
  authors: [{ name: 'PixelSeek Team' }],
  keywords: ['image search', 'AI', 'visual search', 'media search', 'PixelSeek'],
};

export const viewport: Viewport = {
  themeColor: '#121212',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#121212] min-h-screen text-white`}>
        <Providers>
          <TopBar />
          <main className="h-full">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
