'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import SearchBar from '@/components/SearchBar';

export default function LandingPage() {
  const router = useRouter();

  const handleSearch = (searchTerm: string) => {
    router.push(`/home?search=${encodeURIComponent(searchTerm)}`);
  };

  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col justify-center items-center px-4 relative bg-[#121212]">
      <div className="absolute inset-0 z-0 opacity-20">
        <div className="relative w-full h-full">
          <Image
            src="https://same-assets.com/images/blur-bg.jpg"
            alt="Background"
            fill
            className="object-cover"
            priority
          />
        </div>
      </div>

      <div className="z-10 text-center mb-12">
        <h1 className="text-5xl md:text-6xl font-bold mb-4 text-[#daec46]">
          The Search Engine For Creative People
        </h1>
        <p className="text-lg text-gray-300 max-w-2xl mx-auto">
          PixelSeek helps you find the perfect image to express your ideas
          so you can be more efficient in your creative process
        </p>
      </div>

      <div className="z-10 w-full max-w-3xl">
        <SearchBar onSearch={handleSearch} />
      </div>

      <div className="mt-20 z-10 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 max-w-6xl mx-auto">
        {/* Display some sample images */}
        {Array(12).fill(0).map((_, index) => (
          <div
            key={index}
            className="aspect-video bg-[#1a1a1a] rounded-md overflow-hidden cursor-pointer hover:scale-105 transition-transform duration-300"
            onClick={() => router.push('/detail/sample')}
          >
            <div className="w-full h-full relative">
              <Image
                src={`https://same-assets.com/images/sample-frame-${(index % 6) + 1}.jpg`}
                alt={`Sample frame ${index + 1}`}
                fill
                className="object-cover"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
