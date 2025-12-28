import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                background: {
                    primary: '#0f172a',    // Slate-900
                    secondary: '#1e293b',  // Slate-800
                    tertiary: '#334155',   // Slate-700
                },
                accent: {
                    gold: '#f59e0b',       // Amber-500
                    goldHover: '#d97706',  // Amber-600
                    goldLight: '#fbbf24',  // Amber-400
                },
                text: {
                    primary: '#f8faf c',   // Slate-50
                    secondary: '#cbd5e1',  // Slate-300
                    muted: '#94a3b8',      // Slate-400
                },
                success: '#10b981',      // Green-500
                error: '#ef4444',        // Red-500
                warning: '#f59e0b',      // Amber-500
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
            },
        },
    },
    plugins: [],
}

export default config
