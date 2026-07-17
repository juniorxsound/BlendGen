import type { MetadataRoute } from 'next';
import { source } from '@/lib/source';
import { absoluteUrl } from '@/lib/site';

export default function sitemap(): MetadataRoute.Sitemap {
  return source.getPages().map((page) => ({
    url: absoluteUrl(page.url),
    changeFrequency: page.url === '/' ? 'weekly' : 'monthly',
    priority: page.url === '/' ? 1 : page.url.startsWith('/getting-started') ? 0.9 : 0.7,
  }));
}
