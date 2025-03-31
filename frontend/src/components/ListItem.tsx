'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

interface ListItemProps {
  id: string;
  imageUrl: string;
  title?: string;
  director?: string;
  year?: number;
  tags?: string[];
  techniqueInfo?: string[];
  onClick?: (id: string) => void;
}

const ListItem = ({
  id,
  imageUrl,
  title,
  director,
  year,
  tags,
  techniqueInfo,
  onClick,
}: ListItemProps) => {
  const handleClick = () => {
    if (onClick) {
      onClick(id);
    }
  };

  return (
    <div
      className="relative overflow-hidden cursor-pointer transition-transform duration-200 hover:scale-[1.02]"
      onClick={handleClick}
    >
      <Link href={`/detail/${id}`}>
        <div className="relative aspect-video w-full overflow-hidden rounded-md">
          <Image
            src={imageUrl}
            alt={title || 'Frame'}
            width={800}
            height={450}
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover w-full h-full"
          />
        </div>

        {(title || director || year) && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 text-white">
            {title && <p className="font-medium text-sm">{title}</p>}
            {director && (
              <p className="text-xs opacity-80">
                {director}{year ? ` (${year})` : ''}
              </p>
            )}
          </div>
        )}

        {tags && tags.length > 0 && (
          <div className="absolute top-2 right-2 flex gap-1">
            {tags.map((tag, index) => (
              <span
                key={index}
                className="bg-black/60 text-white text-xs px-2 py-0.5 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {techniqueInfo && techniqueInfo.length > 0 && (
          <div className="absolute top-2 left-2">
            <div className="flex gap-1">
              {techniqueInfo.map((technique, index) => (
                <span
                  key={index}
                  className="bg-[#f2ca00] text-black text-xs px-2 py-0.5 rounded"
                >
                  {technique}
                </span>
              ))}
            </div>
          </div>
        )}
      </Link>
    </div>
  );
};

export default ListItem;
