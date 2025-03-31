'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import SideBar from '@/components/SideBar';
import ListItem from '@/components/ListItem';

// Dummy data for list items
const dummyFrames = [
  {
    id: '1',
    imageUrl: 'https://picsum.photos/800/450?random=1',
    title: 'Doctor Strange in the Multiverse of Madness',
    director: 'Tyler Okonma',
    year: 2017,
    tags: ['Girl', 'Fahsion', 'Double Expose', 'Sexy', 'Moco'],
    techniqueInfo: ['Flash Cut', 'Zoom Out'],
  },
  {
    id: '2',
    imageUrl: 'https://picsum.photos/800/450?random=2',
    title: 'Tyler, The Creator - Who Dat Boy',
    director: 'Tyler Okonma',
    year: 2017,
    tags: ['Girl', 'Moco'],
    techniqueInfo: ['Flash Cut'],
  },
  {
    id: '3',
    imageUrl: 'https://picsum.photos/800/450?random=3',
    title: 'Echo Print',
    director: 'Luis Perez',
    year: 2020,
    tags: ['Double Expose'],
    techniqueInfo: ['Trail Printing', 'Accordion Blur'],
  },
  {
    id: '4',
    imageUrl: 'https://picsum.photos/800/450?random=4',
    title: 'Personal Save',
    director: 'Swift',
    year: 2021,
    tags: ['Girl', 'Fahsion'],
    techniqueInfo: ['Zoom Out'],
  },
  {
    id: '5',
    imageUrl: 'https://picsum.photos/800/450?random=5',
    title: 'Girl Eyes',
    director: 'Tyler Okonma',
    year: 2019,
    tags: ['Girl', 'Fahsion', 'Sexy'],
    techniqueInfo: ['Flash Cut', 'Zoom Out'],
  },
  {
    id: '6',
    imageUrl: 'https://picsum.photos/800/450?random=6',
    title: 'Euphoria',
    director: 'Sam Levinson',
    year: 2022,
    tags: ['Girl', 'Moco'],
    techniqueInfo: ['Double Expose'],
  },
  {
    id: '7',
    imageUrl: 'https://picsum.photos/800/450?random=7',
    title: 'Blade Runner 2049',
    director: 'Denis Villeneuve',
    year: 2017,
    tags: ['Sexy', 'Moco'],
    techniqueInfo: ['Flash Cut'],
  },
  {
    id: '8',
    imageUrl: 'https://picsum.photos/800/450?random=8',
    title: 'The Grand Budapest Hotel',
    director: 'Wes Anderson',
    year: 2014,
    tags: ['Fahsion'],
    techniqueInfo: ['Zoom Out'],
  },
];

export default function ListPage() {
  const searchParams = useSearchParams();
  const tag = searchParams.get('tag');
  const technique = searchParams.get('technique');
  const [filteredFrames, setFilteredFrames] = useState(dummyFrames);

  useEffect(() => {
    if (tag) {
      // Filter by tag
      const filtered = dummyFrames.filter(frame =>
        frame.tags.some(t => t.toLowerCase() === tag.toLowerCase())
      );
      setFilteredFrames(filtered);
    } else if (technique) {
      // Filter by technique
      const filtered = dummyFrames.filter(frame =>
        frame.techniqueInfo.some(t => t.toLowerCase() === technique.toLowerCase())
      );
      setFilteredFrames(filtered);
    } else {
      // No filter, return all
      setFilteredFrames(dummyFrames);
    }
  }, [tag, technique]);

  // Get the filter title
  const getTitle = () => {
    if (tag) return `Frames tagged with "${tag}"`;
    if (technique) return `Frames using "${technique}" technique`;
    return "All Frames";
  };

  return (
    <div className="flex min-h-screen bg-[#121212]">
      <SideBar />

      <div className="flex-1 p-6">
        <h1 className="text-[#daec46] text-3xl font-bold mb-2">
          {getTitle()}
        </h1>

        <div className="text-gray-300 mb-6">
          <p>Showing {filteredFrames.length} frames</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredFrames.map((frame) => (
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

        {filteredFrames.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-xl text-white mb-2">No frames found</h3>
            <p className="text-gray-400">
              Try a different filter or check your search criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
