'use client';

import React, { useState } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';

interface SearchBarProps {
  onSearch?: (searchTerm: string) => void;
  defaultValue?: string;
  showColorSearch?: boolean;
  showImageSearch?: boolean;
}

const SearchBar = ({
  onSearch,
  defaultValue = '',
  showColorSearch = true,
  showImageSearch = true,
}: SearchBarProps) => {
  const [searchTerm, setSearchTerm] = useState(defaultValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && searchTerm.trim()) {
      onSearch(searchTerm);
    }
  };

  return (
    <div className="flex flex-col items-center w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="w-full flex flex-col gap-3">
        <div className="flex items-center gap-2 w-full">
          <span className="p-input-icon-left flex-1 w-full">
            <i className="pi pi-search" />
            <InputText
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by Prompt"
              className="w-full bg-[#222222] border-none rounded-md p-3"
            />
          </span>
          {searchTerm && (
            <Button
              icon="pi pi-times"
              type="button"
              className="bg-transparent border-none hover:bg-[#333333]"
              onClick={() => setSearchTerm('')}
            />
          )}
        </div>

        <div className="flex items-center justify-center gap-4">
          {showColorSearch && (
            <Button
              type="button"
              className="bg-transparent border-1 border-[#333333] flex items-center"
            >
              <i className="pi pi-palette mr-2"></i>
              <span>Search by Color</span>
            </Button>
          )}

          {showImageSearch && (
            <Button
              type="button"
              icon="pi pi-image"
              label="Search by IMG"
              className="px-4 py-2 bg-transparent border-1 border-[#f2ca00] text-[#f2ca00] hover:bg-[#f2ca00] hover:text-black"
            />
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchBar;
