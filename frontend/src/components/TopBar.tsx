'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';

const TopBar = () => {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      router.push(`/home?search=${encodeURIComponent(searchTerm)}`);
    }
  };

  return (
    <header className="flex items-center justify-between px-4 py-3 bg-[#121212] text-white">
      <Link href="/" className="font-bold text-2xl text-white">
        LOGO
      </Link>

      <div className="flex items-center gap-2 flex-1 max-w-lg mx-4">
        <form onSubmit={handleSearch} className="flex-1 flex">
          <span className="p-input-icon-left flex-1">
            <i className="pi pi-search" />
            <InputText
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by Prompt"
              className="w-full bg-[#222222] border-none rounded-md"
            />
          </span>
          <Button
            icon="pi pi-times"
            className="ml-1 bg-transparent border-none hover:bg-[#333333]"
            onClick={() => setSearchTerm('')}
          />
        </form>
        <span className="text-gray-400">or</span>
        <Button className="bg-transparent border-1 border-[#333333] flex items-center">
          <i className="pi pi-palette mr-2"></i>
          <span>Search by Color</span>
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <Button
          icon="pi pi-image"
          label="Search by IMG"
          className="px-3 py-2 bg-transparent border-1 border-[#f2ca00] text-[#f2ca00] hover:bg-[#f2ca00] hover:text-black"
        />
        <Link href="/login" className="text-white hover:underline">
          Login
        </Link>
        <div className="px-3 py-1 rounded-full bg-[#333333] text-sm">
          1/10 Searches
        </div>
        <div className="w-8 h-8 rounded-full bg-gray-700"></div>
        <Button
          icon="pi pi-ellipsis-v"
          className="p-button-rounded p-button-text text-white"
        />
      </div>
    </header>
  );
};

export default TopBar;
