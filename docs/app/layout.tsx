import type { Metadata, Viewport } from 'next';
import { RootProvider } from 'fumadocs-ui/provider/next';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';
import { Analytics } from '@vercel/analytics/next';
import { SITE_DESCRIPTION, SITE_NAME, SITE_URL } from '@/lib/site';
import './global.css';

export const metadata: Metadata = {
  metadataBase: SITE_URL,
  title: {
    default: 'BlendGen - Synthetic datasets with Blender',
    template: '%s - BlendGen Docs',
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  authors: [{ name: 'Or Fleisher', url: 'https://orfleisher.com' }],
  creator: 'Or Fleisher',
  publisher: 'BlendGen',
  category: 'Developer documentation',
  keywords: [
    'BlendGen',
    'Blender synthetic data',
    'computer vision datasets',
    'synthetic dataset generation',
    'Blender Python',
    'depth maps',
    'optical flow',
    'image segmentation',
    'machine learning data',
  ],
  alternates: { canonical: '/' },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    siteName: SITE_NAME,
    title: 'BlendGen - Synthetic datasets with Blender',
    description: SITE_DESCRIPTION,
    images: [
      {
        url: '/media/character-dataset-social.gif',
        width: 800,
        height: 300,
        alt: 'Animated BlendGen color, depth, optical flow, normals, alpha, and pose outputs',
        type: 'image/gif',
      },
      {
        url: '/media/character-dataset-poster.jpg',
        width: 1728,
        height: 648,
        alt: 'BlendGen color, depth, optical flow, normals, alpha, and pose outputs',
        type: 'image/jpeg',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BlendGen - Synthetic datasets with Blender',
    description: SITE_DESCRIPTION,
    images: [
      '/media/character-dataset-social.gif',
      '/media/character-dataset-poster.jpg',
    ],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
      'max-video-preview': -1,
    },
  },
};

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f5f5f5' },
    { media: '(prefers-color-scheme: dark)', color: '#111111' },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable}`}
      suppressHydrationWarning
    >
      <body className="flex min-h-screen flex-col font-sans antialiased">
        <RootProvider>{children}</RootProvider>
        <Analytics />
      </body>
    </html>
  );
}
