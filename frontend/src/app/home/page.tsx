'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import SideBar from '@/components/SideBar';
import ListItem from '@/components/ListItem';

// Dummy data representing search results
const dummyFrames = [
  {
    id: '1',
    imageUrl: 'https://same-assets.com/images/sample-frame-1.jpg',
    title: 'Doctor Strange in the Multiverse of Madness',
    director: 'Tyler Okonma',
    year: 2017,
    tags: ['Girl', 'Fahsion', 'Double Expose', 'Sexy', 'Moco'],
    techniqueInfo: ['Flash Cut', 'Zoom Out'],
  },
  {
    id: '2',
    imageUrl: 'https://same-assets.com/images/sample-frame-2.jpg',
    title: 'Tyler, The Creator - Who Dat Boy',
    director: 'Tyler Okonma',
    year: 2017,
    tags: ['Girl', 'Moco'],
    techniqueInfo: ['Flash Cut'],
  },
  {
    id: '3',
    imageUrl: 'https://same-assets.com/images/sample-frame-3.jpg',
    title: 'Echo Print',
    director: 'Luis Perez',
    year: 2020,
    tags: ['Double Expose'],
    techniqueInfo: ['Trail Printing', 'Accordion Blur'],
  },
  {
    id: '4',
    imageUrl: 'https://same-assets.com/images/sample-frame-4.jpg',
    title: 'Personal Save',
    director: 'Swift',
    year: 2021,
    tags: ['Girl', 'Fahsion'],
    techniqueInfo: ['Zoom Out'],
  },
  {
    id: '5',
    imageUrl: 'https://same-assets.com/images/sample-frame-5.jpg',
    title: 'Girl Eyes',
    director: 'Tyler Okonma',
    year: 2019,
    tags: ['Girl', 'Fahsion', 'Sexy'],
    techniqueInfo: ['Flash Cut', 'Zoom Out'],
  },
  {
    id: '6',
    imageUrl: 'https://same-assets.com/images/sample-frame-6.jpg',
    title: 'Euphoria',
    director: 'Sam Levinson',
    year: 2022,
    tags: ['Girl', 'Moco'],
    techniqueInfo: ['Double Expose'],
  },
];

export default function HomePage() {
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get('search') || '';
  const [searchResults, setSearchResults] = useState(dummyFrames);

  // Simulate filtering based on search query
  useEffect(() => {
    if (searchQuery) {
      const filteredResults = dummyFrames.filter(frame =>
        frame.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        frame.director.toLowerCase().includes(searchQuery.toLowerCase()) ||
        frame.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setSearchResults(filteredResults);
    } else {
      setSearchResults(dummyFrames);
    }
  }, [searchQuery]);

  return (
    <div className="flex min-h-screen bg-[#121212]">
      <SideBar />

      <div className="flex-1 p-6">
        {searchQuery ? (
          <h1 className="text-[#daec46] text-3xl font-bold mb-2">
            Results for &quot;{searchQuery}&quot;
          </h1>
        ) : (
          <h1 className="text-[#daec46] text-3xl font-bold mb-2">
            Browse Frames
          </h1>
        )}

        <div className="text-gray-300 mb-6">
          {searchResults.length === 0 ? (
            <p>No results found. Try a different search term.</p>
          ) : (
            <p>Results for {searchResults.length} screenshots of {dummyFrames.length}</p>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {searchResults.map((frame) => (
            <ListItem
              key={frame.id}
              id={frame.id}
              imageUrl={frame.imageUrl}
              title={frame.title}
              director={frame.director}
              year={frame.year}
              tags={frame.tags}
              techniqueInfo={frame.techniqueInfo}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
