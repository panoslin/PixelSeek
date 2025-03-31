'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Button } from 'primereact/button';

interface DetailCardProps {
  id: string;
  imageUrl: string;
  title: string;
  description?: string;
  director?: string;
  dop?: string; // Director of Photography
  colorist?: string;
  tags?: string[];
  techniqueInfo?: string[];
  year?: number;
  similarFrames?: {id: string; imageUrl: string}[];
  onPlay?: () => void;
  onSave?: () => void;
}

const DetailCard = ({
  id,
  imageUrl,
  title,
  description,
  director,
  dop,
  colorist,
  tags = [],
  techniqueInfo = [],
  year,
  similarFrames = [],
  onPlay,
  onSave,
}: DetailCardProps) => {
  return (
    <div className="bg-[#121212] text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#daec46] mb-2">{title}</h1>
          {description && (
            <p className="text-gray-300 text-sm max-w-3xl mb-4">{description}</p>
          )}

          <div className="flex flex-wrap items-center gap-2 mb-4">
            {tags.map((tag, index) => (
              <Link
                href={`/list?tag=${encodeURIComponent(tag)}`}
                key={index}
                className="text-sm text-gray-300 hover:text-white hover:underline"
              >
                {tag}
              </Link>
            ))}
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <div className="relative aspect-video w-full overflow-hidden rounded-lg">
              <Image
                src={imageUrl}
                alt={title}
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                className="object-cover"
              />
            </div>

            <div className="flex justify-between items-center mt-4">
              <Button
                icon="pi pi-play"
                label="Play"
                onClick={onPlay}
                className="px-6 py-2 bg-[#daec46] text-black hover:bg-[#c5d73e] rounded-full"
              />

              <div className="flex gap-3">
                <Button
                  icon="pi pi-download"
                  className="p-button-rounded p-button-text text-white"
                />
                <Button
                  icon="pi pi-bookmark"
                  label="Save it"
                  onClick={onSave}
                  className="bg-transparent border-1 border-[#daec46] text-[#daec46] hover:bg-[#daec46] hover:text-black"
                />
              </div>
            </div>
          </div>

          <div className="lg:w-1/3">
            <div className="bg-[#1a1a1a] rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold mb-3">Film Information</h3>

              <div className="flex flex-col gap-2">
                {techniqueInfo.length > 0 && (
                  <div className="flex gap-2 mb-2">
                    <span className="text-gray-400">Technique -</span>
                    <div className="flex flex-wrap gap-1">
                      {techniqueInfo.map((technique, index) => (
                        <span key={index} className="text-[#daec46]">{technique}</span>
                      ))}
                    </div>
                  </div>
                )}

                {director && (
                  <div className="flex">
                    <span className="text-gray-400 w-24">Director</span>
                    <span>{director}</span>
                  </div>
                )}

                {dop && (
                  <div className="flex">
                    <span className="text-gray-400 w-24">DOP</span>
                    <span>{dop}</span>
                  </div>
                )}

                {colorist && (
                  <div className="flex">
                    <span className="text-gray-400 w-24">Colorist</span>
                    <span>{colorist}</span>
                  </div>
                )}
              </div>
            </div>

            {similarFrames.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-3">Similar Frames</h3>
                <div className="grid grid-cols-3 gap-2">
                  {similarFrames.map((frame, index) => (
                    <Link key={index} href={`/detail/${frame.id}`}>
                      <div className="relative aspect-square overflow-hidden rounded">
                        <Image
                          src={frame.imageUrl}
                          alt="Similar frame"
                          fill
                          className="object-cover hover:opacity-80 transition-opacity"
                        />
                      </div>
                    </Link>
                  ))}
                </div>
                <div className="flex justify-center mt-4">
                  <Button
                    icon="pi pi-search"
                    label="Find Similar"
                    className="bg-transparent border-none text-white hover:bg-[#333333]"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailCard;
