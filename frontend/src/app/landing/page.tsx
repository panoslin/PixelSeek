'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { Button } from 'primereact/button';
import SearchBar from '@/components/SearchBar';

export default function LandingPage() {
  const router = useRouter();

  const handleSearch = (searchTerm: string) => {
    router.push(`/home?search=${encodeURIComponent(searchTerm)}`);
  };

  const features = [
    {
      icon: 'pi-search',
      title: 'Smart Search',
      description: 'Find exactly what you need with our powerful search engine that understands the language of filmmaking.'
    },
    {
      icon: 'pi-palette',
      title: 'Color Search',
      description: 'Search frames based on color palettes to find the perfect visual reference for your projects.'
    },
    {
      icon: 'pi-image',
      title: 'Image Search',
      description: 'Upload an image and find visually similar frames from thousands of films and videos.'
    },
    {
      icon: 'pi-tag',
      title: 'Advanced Filtering',
      description: 'Filter by technique, aspect ratio, time of day, and more to narrow down your search results.'
    },
    {
      icon: 'pi-bookmark',
      title: 'Save Collections',
      description: 'Create personal collections of frames to reference in your creative projects.'
    },
    {
      icon: 'pi-download',
      title: 'High Quality Downloads',
      description: 'Download high-resolution frames for use in mood boards, presentations, and more.'
    },
  ];

  return (
    <div className="bg-[#121212] text-white">
      {/* Hero section */}
      <section className="min-h-[80vh] flex flex-col justify-center items-center px-4 relative overflow-hidden">
        {/* Background overlay with blurred images */}
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

        <div className="z-10 text-center mb-12 max-w-4xl">
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 text-[#daec46]">
            The Search Engine<br />For Creative People
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
            PixelSeek helps you find the perfect image to express your ideas
            so you can be more efficient in your creative process
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              label="Get Started"
              icon="pi pi-arrow-right"
              className="px-6 py-3 bg-[#daec46] text-black text-lg font-medium hover:bg-[#c5d73e]"
              onClick={() => router.push('/home')}
            />
            <Button
              label="Learn More"
              className="px-6 py-3 border-2 border-white text-white text-lg font-medium hover:bg-white/10"
              onClick={() => {
                const featuresSection = document.getElementById('features');
                featuresSection?.scrollIntoView({ behavior: 'smooth' });
              }}
            />
          </div>
        </div>

        <div className="z-10 w-full max-w-3xl mt-8">
          <SearchBar onSearch={handleSearch} />
        </div>
      </section>

      {/* Features section */}
      <section id="features" className="py-20 px-4 bg-[#0a0a0a]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-[#daec46]">
              Features
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need to find the perfect visual reference for your creative projects
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="p-6 bg-[#1a1a1a] rounded-lg hover:bg-[#222222] transition-colors"
              >
                <div className="text-[#daec46] text-3xl mb-4">
                  <i className={`pi ${feature.icon}`}></i>
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing CTA section */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4 text-[#daec46]">
            Ready to Elevate Your Creative Process?
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
            Join thousands of filmmakers, directors, and creative professionals who use PixelSeek to find visual inspiration
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              label="Start For Free"
              className="px-6 py-3 bg-[#daec46] text-black text-lg font-medium hover:bg-[#c5d73e]"
              onClick={() => router.push('/home')}
            />
            <Button
              label="View Pricing"
              className="px-6 py-3 border-2 border-[#daec46] text-[#daec46] text-lg font-medium hover:bg-[#daec46] hover:text-black"
              onClick={() => router.push('/payment')}
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 bg-[#0a0a0a] border-t border-[#333333]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">PixelSeek</h3>
            <p className="text-gray-400 mb-4">
              The ultimate search engine for creative professionals looking for visual references.
            </p>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-400">
              <li><Link href="/home" className="hover:text-[#daec46]">Search</Link></li>
              <li><Link href="/payment" className="hover:text-[#daec46]">Pricing</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">API</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Integrations</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-gray-400">
              <li><Link href="#" className="hover:text-[#daec46]">Blog</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Tutorials</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Support</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Documentation</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-gray-400">
              <li><Link href="#" className="hover:text-[#daec46]">About Us</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Careers</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Contact</Link></li>
              <li><Link href="#" className="hover:text-[#daec46]">Privacy Policy</Link></li>
            </ul>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-12 pt-8 border-t border-[#333333] text-center text-gray-500">
          <p>© {new Date().getFullYear()} PixelSeek. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
