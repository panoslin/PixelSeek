'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

export default function LandingPage() {
  const router = useRouter();

  // Sample images with varying sizes for the mosaic layout
  const sampleImages = [
    {
      id: 'photo-1506744038136-46273834b3fb',
      size: 'wide',
      category: 'landscape'
    },
    {
      id: 'photo-1487958449943-2429e8be8625',
      size: 'wide',
      category: 'architecture'
    },
    {
      id: 'photo-1518770660439-4636190af475',
      size: 'square',
      category: 'portrait'
    },
    {
      id: 'photo-1438761681033-6461ffad8d80',
      size: 'square',
      category: 'portrait'
    },
    {
      id: 'photo-1416331108676-a22ccb276e35',
      size: 'square',
      category: 'portrait'
    },
    {
      id: 'photo-1504674900247-0877df9cc836',
      size: 'square',
      category: 'portrait'
    }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a]">

      {/* Main Content */}
      <main className="pt-32 px-6">
        <div className="max-w-[1200px] mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-[#daec46] text-6xl font-bold mb-4 leading-tight">
              The Search Engine For Creative People
            </h1>
            <p className="text-[#daec46] text-xl opacity-80">
              FrameSeeks helps you find the perfect image to express your ideas<br />
              so you can be more efficient in your creative process
            </p>
          </div>

          {/* Search Section */}
          <div className="max-w-[800px] mx-auto mb-20">
            <div className="flex gap-3 items-center">
              <div className="flex-1 relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Search by Prompt"
                  className="w-full bg-[#1a1a1a] rounded-lg pl-12 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#daec46]/30"
                />
              </div>
              <span className="text-gray-600">or</span>
              <button className="flex items-center gap-2 bg-[#1a1a1a] rounded-lg px-4 py-3 text-white hover:bg-[#252525] transition-colors">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                  <path d="M12 8v8M8 12h8" strokeWidth="2"/>
                </svg>
                <span>Search by Color</span>
              </button>
            </div>
          </div>

          {/* Image Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sampleImages.map((image, index) => (
              <div
                key={index}
                className={`group relative w-full cursor-pointer
                  ${image.size === 'wide' ? 'aspect-[3/2]' : 'aspect-square'}`}
              >
                <div className="absolute inset-0 rounded-lg overflow-hidden">
                  <div className="relative w-full h-full">
                    <Image
                      src={`https://images.unsplash.com/${image.id}?w=1200&h=${image.size === 'wide' ? '800' : '600'}&fit=crop&q=90`}
                      alt={`${image.category} image`}
                      fill
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                      sizes="(max-width: 768px) 100vw, 50vw"
                      priority={index < 4}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
