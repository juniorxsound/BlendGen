import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export function baseOptions(): BaseLayoutProps {
  return {
    nav: { title: 'BlendGen' },
    githubUrl: 'https://github.com/juniorxsound/BlendGen',
    links: [
      { text: 'Guides', url: '/docs/guides' },
      { text: 'API', url: '/docs/api' },
    ],
  };
}
