/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.watchOptions = {
      ignored: ['**/.git/**', '**/node_modules/**', '**/data/**', '**/.next/**', '**/.venv/**'],
    };
    return config;
  },
};

module.exports = nextConfig;
