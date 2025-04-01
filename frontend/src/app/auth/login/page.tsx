"use client";

import React, {useState, useEffect} from "react";
import {useRouter, useSearchParams} from "next/navigation";
import Link from "next/link";
import {InputText} from "primereact/inputtext";
import {Password} from "primereact/password";
import {Button} from "primereact/button";
import {Checkbox, CheckboxChangeEvent} from "primereact/checkbox";
import {Divider} from "primereact/divider";
import {classNames} from "primereact/utils";
import {Message} from "primereact/message";
import {Toast} from "primereact/toast";
import {useAuth} from "@/context/AuthContext";
import styles from "./page.module.css";

// API URL would be defined in an environment variable in production
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function LoginPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const {login} = useAuth();
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        rememberMe: false,
    });
    const [errors, setErrors] = useState<{email?: string; password?: string}>({});
    const [loading, setLoading] = useState(false);
    const [loginError, setLoginError] = useState("");
    const toast = React.useRef<Toast>(null);

    // Check for callback params from OAuth providers
    useEffect(() => {
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const error = searchParams.get("error");

        if (error) {
            toast.current?.show({
                severity: "error",
                summary: "Authentication Error",
                detail: "Failed to authenticate with the provider",
                life: 5000,
            });
            return;
        }

        if (code && state) {
            // Handle OAuth callback
            const provider = localStorage.getItem("oauth_provider");
            handleOAuthCallback(code, state, provider || "");
        }
    }, [searchParams]);

    const handleOAuthCallback = async (code: string, state: string, provider: string) => {
        try {
            setLoading(true);

            const endpoint =
                provider === "google"
                    ? `${API_URL}/users/auth/google/callback/`
                    : `${API_URL}/users/auth/wechat/callback/`;

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({code, state}),
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Failed to authenticate");
            }

            const data = await response.json();

            // Use the AuthContext login method
            if (data.access) {
                await login({
                    access: data.access,
                    refresh: data.refresh || "",
                });

                // Remove the oauth provider from storage
                localStorage.removeItem("oauth_provider");

                // Redirect to home
                router.push("/home");
            }
        } catch (error) {
            console.error("OAuth callback error:", error);
            toast.current?.show({
                severity: "error",
                summary: "Authentication Error",
                detail: "Failed to complete authentication",
                life: 5000,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setFormData((prev) => ({...prev, [name]: value}));

        // Clear errors when user types
        if (errors[name as keyof typeof errors]) {
            setErrors((prev) => ({...prev, [name]: undefined}));
        }
    };

    const handleCheckboxChange = (e: CheckboxChangeEvent) => {
        setFormData((prev) => ({...prev, rememberMe: e.checked ?? false}));
    };

    const validateForm = () => {
        const newErrors: {email?: string; password?: string} = {};

        if (!formData.email) {
            newErrors.email = "Email is required";
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = "Email format is invalid";
        }

        if (!formData.password) {
            newErrors.password = "Password is required";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoginError("");

        if (!validateForm()) return;

        setLoading(true);
        try {
            // Make the actual login API call
            const response = await fetch(`${API_URL}/token/`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    email: formData.email,
                    password: formData.password,
                }),
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Invalid credentials");
            }

            const data = await response.json();

            // Use the AuthContext login method
            await login({
                access: data.access,
                refresh: data.refresh || "",
            });

            // If remember me is checked, store the preference
            if (formData.rememberMe) {
                localStorage.setItem("remember_me", "true");
            }

            // Redirect to home page
            router.push("/home");
        } catch (error) {
            setLoginError("Invalid email or password. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleSocialLogin = (provider: string) => {
        // Store the provider to use during callback
        localStorage.setItem("oauth_provider", provider);

        // Redirect to the backend OAuth endpoint
        window.location.href = `${API_URL}/users/auth/${provider}/login/`;
    };

    const socialLogins = [
        {name: "Google", icon: "pi pi-google", color: "#DB4437", provider: "google"},
        {name: "WeChat", icon: "pi pi-comments", color: "#07C160", provider: "wechat"},
    ];

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#121212] p-4">
            <Toast ref={toast} position="top-center" />

            <div className="w-full max-w-md bg-[#1a1a1a] rounded-lg shadow-lg p-6">
                <div className="text-center mb-6">
                    <h1 className="text-3xl font-bold text-white mb-2">Login to PixelSeek</h1>
                    <p className="text-gray-400">Access your saved frames and personalized searches</p>
                </div>

                {loginError && <Message severity="error" text={loginError} className="w-full mb-4" />}

                <div className="flex flex-column gap-2 mb-4">
                    {socialLogins.map((social) => (
                        <Button
                            key={social.name}
                            icon={social.icon}
                            label={`Continue with ${social.name}`}
                            onClick={() => handleSocialLogin(social.provider)}
                            className={styles.socialButton}
                            aria-label={`Sign in with ${social.name}`}
                        />
                    ))}
                </div>
                
                <Divider align="center" className={styles.divider}>
                    <span className="text-gray-400 text-sm">or continue with</span>
                </Divider>

                <form onSubmit={handleLogin} className="space-y-4" noValidate>
                    <div className="flex flex-col gap-1">
                        <span className="p-float-label">
                            <InputText
                                id="email"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                className={classNames("w-full bg-[#222222] border-[#333333] py-2 px-2", {
                                    "p-invalid": errors.email,
                                })}
                                aria-describedby="email-error"
                                required
                            />
                            <label htmlFor="email" className="text-gray-400">
                                Email
                            </label>
                        </span>
                        {errors.email && (
                            <small id="email-error" className="p-error text-xs">
                                {errors.email}
                            </small>
                        )}
                    </div>

                    <div className="flex flex-col gap-1">
                        <span className="p-float-label">
                            <div className={styles.password_container}>
                                <Password
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    toggleMask
                                    feedback={false}
                                    className={classNames("w-full", {
                                        "p-invalid": errors.password,
                                    })}
                                    inputClassName="w-full bg-[#222222] border-[#333333] py-2 px-2"
                                    aria-describedby="password-error"
                                    required
                                />
                            </div>
                            <label htmlFor="password" className="text-gray-400">
                                Password
                            </label>
                        </span>
                        {errors.password && (
                            <small id="password-error" className="p-error text-xs">
                                {errors.password}
                            </small>
                        )}
                    </div>

                    <div className="flex justify-between items-center">
                        <div className="p-field-checkbox flex items-center">
                            <Checkbox
                                inputId="rememberMe"
                                name="rememberMe"
                                checked={formData.rememberMe}
                                onChange={handleCheckboxChange}
                                className="mr-2 pixelseek-rememberme-checkbox"
                            />
                            <label htmlFor="rememberMe" className="text-gray-300 cursor-pointer text-sm">
                                Remember me
                            </label>
                        </div>

                        <Link href="/auth/forgot-password" className="text-[#daec46] text-sm hover:underline">
                            Forgot password?
                        </Link>
                    </div>
                    <Button
                        type="submit"
                        label="Login"
                        icon={loading ? "pi pi-spin pi-spinner" : "pi pi-sign-in"}
                        iconPos="right"
                        className="w-full bg-[#daec46] text-black hover:bg-[#c5d73e] font-medium px-4 py-2"
                        disabled={loading}
                    />
                </form>

                <div className="mt-6 text-center">
                    <span className="text-gray-400">Don&apos;t have an account? </span>
                    <Link href="/auth/signup" className="text-[#daec46] hover:underline font-medium">
                        Sign up
                    </Link>
                </div>
            </div>
        </div>
    );
}
