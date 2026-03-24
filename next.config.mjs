/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "export",
  basePath: process.env.PAGES_BASE_PATH || "",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
