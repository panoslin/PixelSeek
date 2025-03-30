'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import DetailCard from '@/components/DetailCard';

interface FrameData {
  id: string;
  imageUrl: string;
  title: string;
  description?: string;
  director?: string;
  dop?: string;
  colorist?: string;
  tags: string[];
  techniqueInfo: string[];
  year?: number;
  similarFrames: Array<{id: string; imageUrl: string}>;
}

interface FramesDataType {
  [key: string]: FrameData;
}

// Dummy data for the detail view
const framesData: FramesDataType = {
  '1': {
    id: '1',
    imageUrl: 'https://same-assets.com/images/sample-frame-1.jpg',
    title: 'Doctor Strange in the Multiverse of Madness',
    description: 'Also known as \'trail printing\' or \'accordion blur\' — this variation of the motion blur involves leaving behind a trail of footage for a second before it catches back up with the shot. It\'s reminiscent of the practical Step-printing technique of which it gets its namesake.',
    director: 'Tyler Okonma',
    dop: 'Luis Perez',
    colorist: 'Swift',
    tags: ['Girl', 'Fahsion', 'Double Expose', 'Sexy', 'Moco'],
    techniqueInfo: ['Flash Cut', 'Zoom Out'],
    year: 2017,
    similarFrames: [
      {id: '2', imageUrl: 'https://same-assets.com/images/sample-frame-2.jpg'},
      {id: '3', imageUrl: 'https://same-assets.com/images/sample-frame-3.jpg'},
      {id: '4', imageUrl: 'https://same-assets.com/images/sample-frame-4.jpg'},
      {id: '5', imageUrl: 'https://same-assets.com/images/sample-frame-5.jpg'},
      {id: '6', imageUrl: 'https://same-assets.com/images/sample-frame-6.jpg'},
    ]
  },
  '2': {
    id: '2',
    imageUrl: 'https://same-assets.com/images/sample-frame-2.jpg',
    title: 'Tyler, The Creator - Who Dat Boy',
    description: 'Flash cut zoom out, starting close up and ending on a wide.',
    director: 'Tyler Okonma',
    dop: 'Luis Perez',
    colorist: 'Swift',
    tags: ['Girl', 'Moco'],
    techniqueInfo: ['Flash Cut'],
    year: 2017,
    similarFrames: [
      {id: '1', imageUrl: 'https://same-assets.com/images/sample-frame-1.jpg'},
      {id: '3', imageUrl: 'https://same-assets.com/images/sample-frame-3.jpg'},
      {id: '4', imageUrl: 'https://same-assets.com/images/sample-frame-4.jpg'},
      {id: '5', imageUrl: 'https://same-assets.com/images/sample-frame-5.jpg'},
      {id: '6', imageUrl: 'https://same-assets.com/images/sample-frame-6.jpg'},
    ]
  },
  '3': {
    id: '3',
    imageUrl: 'https://same-assets.com/images/sample-frame-3.jpg',
    title: 'Echo Print',
    description: 'Also known as \'trail printing\' or \'accordion blur\' — this variation of the motion blur involves leaving behind a trail of footage for a second before it catches back up with the shot. It\'s reminiscent of the practical Step-printing technique of which it gets its namesake.',
    director: 'Luis Perez',
    dop: 'Tyler Okonma',
    colorist: 'Swift',
    tags: ['Double Expose'],
    techniqueInfo: ['Trail Printing', 'Accordion Blur'],
    year: 2020,
    similarFrames: [
      {id: '1', imageUrl: 'https://same-assets.com/images/sample-frame-1.jpg'},
      {id: '2', imageUrl: 'https://same-assets.com/images/sample-frame-2.jpg'},
      {id: '4', imageUrl: 'https://same-assets.com/images/sample-frame-4.jpg'},
      {id: '5', imageUrl: 'https://same-assets.com/images/sample-frame-5.jpg'},
      {id: '6', imageUrl: 'https://same-assets.com/images/sample-frame-6.jpg'},
    ]
  },
  'sample': {
    id: 'sample',
    imageUrl: 'https://same-assets.com/images/sample-frame-1.jpg',
    title: 'Doctor Strange in the Multiverse of Madness',
    description: 'Also known as \'trail printing\' or \'accordion blur\' — this variation of the motion blur involves leaving behind a trail of footage for a second before it catches back up with the shot. It\'s reminiscent of the practical Step-printing technique of which it gets its namesake.',
    director: 'Tyler Okonma',
    dop: 'Luis Perez',
    colorist: 'Swift',
    tags: ['Girl', 'Fahsion', 'Double Expose', 'Sexy', 'Moco'],
    techniqueInfo: ['Flash Cut', 'Zoom Out'],
    year: 2017,
    similarFrames: [
      {id: '2', imageUrl: 'https://same-assets.com/images/sample-frame-2.jpg'},
      {id: '3', imageUrl: 'https://same-assets.com/images/sample-frame-3.jpg'},
      {id: '4', imageUrl: 'https://same-assets.com/images/sample-frame-4.jpg'},
      {id: '5', imageUrl: 'https://same-assets.com/images/sample-frame-5.jpg'},
      {id: '6', imageUrl: 'https://same-assets.com/images/sample-frame-6.jpg'},
    ]
  }
};

export default function DetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [frameData, setFrameData] = useState<FrameData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call to get frame data
    setLoading(true);
    setTimeout(() => {
      setFrameData(framesData[id] || framesData.sample);
      setLoading(false);
    }, 500);
  }, [id]);

  const handlePlay = () => {
    console.log('Play video');
    // Here you would implement video playback logic
  };

  const handleSave = () => {
    console.log('Save to collection');
    // Here you would implement save logic
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[80vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#daec46]"></div>
      </div>
    );
  }

  if (!frameData) {
    return (
      <div className="flex justify-center items-center min-h-[80vh]">
        <div className="text-center">
          <h2 className="text-2xl text-white mb-4">Frame not found</h2>
          <p className="text-gray-400">The frame you're looking for doesn't exist or was removed.</p>
        </div>
      </div>
    );
  }

  return (
    <DetailCard
      {...frameData}
      onPlay={handlePlay}
      onSave={handleSave}
    />
  );
}
