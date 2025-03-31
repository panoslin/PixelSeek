"use client";

import React, {useState, useRef} from "react";
import {useRouter} from "next/navigation";
import Link from "next/link";
import {InputText} from "primereact/inputtext";
import {Button} from "primereact/button";
import {Avatar} from "primereact/avatar";
import {ProgressBar} from "primereact/progressbar";
import {Menu} from "primereact/menu";
import {MenuItem} from "primereact/menuitem";

const TopBar = () => {
    const router = useRouter();
    const [searchTerm, setSearchTerm] = useState("");
    const menu = useRef<Menu>(null);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchTerm.trim()) {
            router.push(`/home?search=${encodeURIComponent(searchTerm)}`);
        }
    };

    const userMenuItems: MenuItem[] = [
        {
            label: "Profile",
            icon: "pi pi-user",
            command: () => router.push("/profile"),
        },
        {
            label: "Settings",
            icon: "pi pi-cog",
            command: () => router.push("/settings"),
        },
        {separator: true},
        {
            label: "Logout",
            icon: "pi pi-sign-out",
            command: () => console.log("Logout clicked"),
        },
    ];

    return (
        <header className="flex items-center justify-between px-4 py-2 bg-[#121212] text-white">
            <Link href="/" className="font-bold text-2xl text-white mr-2">
                LOGO
            </Link>

            <div className="flex items-center gap-2 flex-1 mx-4">
                <form onSubmit={handleSearch} className="relative w-[550px]">
                    <Button
                        icon="pi pi-trash"
                        className="absolute right-2 top-1/2 -translate-y-1/2 z-10 bg-transparent border-none hover:bg-transparent p-0"
                        onClick={() => setSearchTerm("")}
                    />
                    <InputText
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search by Prompt"
                        className="w-full bg-[#222222] border-none rounded-md pr-8 pl-2 py-2"
                    />
                </form>

                <span className="text-gray-400 mx-3">or</span>

                <Button className="bg-transparent border-none flex items-center p-0 py-2">
                    <i className="pi pi-palette mr-2" style={{color: "#ff00ff"}}></i>
                    <span>Search by Color</span>
                </Button>

                <Button
                    icon="pi pi-image"
                    label="Search by IMG"
                    className="bg-[#7b9f35] border-none hover:bg-[#6b8f25] text-white font-normal px-3 py-2 mx-2"
                />
            </div>

            <div className="flex items-center gap-3">
                <Link href="/auth/login" className="text-white hover:underline ml-4  py-2">
                    Login
                </Link>

                <div className="relative h-7 w-40 ">
                    <ProgressBar
                        value={50}
                        className="h-7 w-40 rounded-full absolute"
                        style={{background: "#333333"}}
                        showValue={false}
                    />
                    <div className="absolute inset-0 flex items-center justify-center text-white text-sm">
                        5/10 Searches
                    </div>
                </div>

                <Avatar
                    className="bg-gray-700 "
                    shape="circle"
                    size="normal"
                    image="https://randomuser.me/api/portraits/women/32.jpg"
                />

                <Menu model={userMenuItems} popup ref={menu} />
                <Button
                    icon="pi pi-ellipsis-v"
                    className="p-button-rounded p-button-text text-white"
                    onClick={(e) => menu.current?.toggle(e)}
                    aria-label="User menu"
                />
            </div>
        </header>
    );
};

export default TopBar;
