import type { Config } from 'tailwindcss';

const config: Config = {
    content: ['./index.html', './src/**/*.{ts,tsx}'],
    theme: {
        extend: {
            colors: {
                ink: '#090d13',
                mist: '#d8e0ee',
                ember: '#ff8c42',
                tide: '#58c4dd',
                moss: '#85c47c',
                panel: '#101722',
            },
            boxShadow: {
                glow: '0 20px 80px rgba(17, 24, 39, 0.35)',
            },
            backgroundImage: {
                haze: 'radial-gradient(circle at top, rgba(88, 196, 221, 0.18), transparent 32%), radial-gradient(circle at bottom right, rgba(255, 140, 66, 0.16), transparent 28%)',
            },
        },
    },
    plugins: [],
};

export default config;