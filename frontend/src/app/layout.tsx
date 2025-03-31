import './globals.css';
import { Inter } from 'next/font/google';
import type { Metadata } from 'next';

// PrimeReact imports
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/lara-dark-indigo/theme.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

import TopBar from '@/components/TopBar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'PixelSeek - The Search Engine For Creative People',
  description: 'Find the perfect film or video frame reference for your creative projects',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#121212] min-h-screen text-white`}>
        <TopBar />
        <main className="h-full">
          {children}
        </main>
      </body>
    </html>
  );
}
