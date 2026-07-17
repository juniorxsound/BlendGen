import { NextRequest, NextResponse } from 'next/server';
import { isMarkdownPreferred } from 'fumadocs-core/negotiation';

function isReservedPath(pathname: string) {
  return (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/llms.mdx/') ||
    pathname === '/api/search' ||
    pathname === '/llms.txt' ||
    pathname === '/llms-full.txt' ||
    pathname === '/favicon.ico' ||
    (/\.[a-z0-9]+$/i.test(pathname) && !pathname.endsWith('.md'))
  );
}

function markdownRoute(pathname: string, stripSuffix = false) {
  const withoutSuffix = stripSuffix ? pathname.slice(0, -3) : pathname;
  const slug = withoutSuffix.replace(/^\/+|\/+$/g, '');
  const normalized = slug === 'index' ? '' : slug;
  return `/llms.mdx/docs/${normalized ? `${normalized}/` : ''}content.md`;
}

export default function proxy(request: NextRequest) {
  if (isReservedPath(request.nextUrl.pathname)) return NextResponse.next();

  if (request.nextUrl.pathname.endsWith('.md')) {
    return NextResponse.rewrite(
      new URL(markdownRoute(request.nextUrl.pathname, true), request.nextUrl),
    );
  }

  if (isMarkdownPreferred(request)) {
    return NextResponse.rewrite(
      new URL(markdownRoute(request.nextUrl.pathname), request.nextUrl),
    );
  }

  return NextResponse.next();
}
