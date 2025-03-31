'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { InputText } from 'primereact/inputtext';
import { Password } from 'primereact/password';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { Divider } from 'primereact/divider';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    // Simulate login API call
    setTimeout(() => {
      setLoading(false);
      router.push('/home');
    }, 1000);
  };

  const socialLogins = [
    { name: 'Google', icon: 'pi pi-google', color: '#DB4437' },
    { name: 'Apple', icon: 'pi pi-apple', color: '#000000' },
    { name: 'Facebook', icon: 'pi pi-facebook', color: '#4267B2' },
    { name: 'Twitter', icon: 'pi pi-twitter', color: '#1DA1F2' },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#121212] p-4">
      <div className="w-full max-w-md bg-[#1a1a1a] rounded-lg shadow-lg p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Login to PixelSeek</h1>
          <p className="text-gray-400">Access your saved frames and personalized searches</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="p-float-label">
            <InputText
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#222222] border-[#333333]"
              required
            />
            <label htmlFor="email" className="text-gray-400">Email</label>
          </div>

          <div className="p-float-label">
            <Password
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              toggleMask
              className="w-full bg-[#222222]"
              inputClassName="w-full bg-[#222222] border-[#333333]"
              required
            />
            <label htmlFor="password" className="text-gray-400">Password</label>
          </div>

          <div className="flex justify-between items-center">
            <div className="p-field-checkbox flex items-center">
              <Checkbox
                inputId="rememberMe"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.checked || false)}
                className="mr-2"
              />
              <label htmlFor="rememberMe" className="text-gray-300 cursor-pointer text-sm">
                Remember me
              </label>
            </div>

            <Link href="/forgot-password" className="text-[#daec46] text-sm hover:underline">
              Forgot password?
            </Link>
          </div>

          <Button
            type="submit"
            label="Login"
            icon={loading ? "pi pi-spin pi-spinner" : "pi pi-sign-in"}
            className="w-full bg-[#daec46] text-black hover:bg-[#c5d73e]"
            disabled={loading}
          />
        </form>

        <Divider align="center">
          <span className="text-gray-400 text-sm">or continue with</span>
        </Divider>

        <div className="grid grid-cols-2 gap-3 mt-4">
          {socialLogins.map((social, index) => (
            <Button
              key={index}
              icon={social.icon}
              label={social.name}
              className="p-button-outlined border-[#333333] text-white hover:border-[#444444]"
              style={{ borderColor: social.color }}
            />
          ))}
        </div>

        <div className="mt-8 text-center">
          <span className="text-gray-400">Don&apos;t have an account? </span>
          <Link href="/signup" className="text-[#daec46] hover:underline">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
