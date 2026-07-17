import { NextRequest, NextResponse } from 'next/server';
import { isMarkdownPreferred, rewritePath } from 'fumadocs-core/negotiation';

const { rewrite: rewriteDocs } = rewritePath(
  '/docs{/*path}',
  '/llms.mdx/docs{/*path}/content.md',
);
const { rewrite: rewriteSuffix } = rewritePath(
  '/docs{/*path}.md',
  '/llms.mdx/docs{/*path}/content.md',
);

export default function proxy(request: NextRequest) {
  const suffixResult = rewriteSuffix(request.nextUrl.pathname);
  if (suffixResult) return NextResponse.rewrite(new URL(suffixResult, request.nextUrl));

  if (isMarkdownPreferred(request)) {
    const acceptResult = rewriteDocs(request.nextUrl.pathname);
    if (acceptResult) return NextResponse.rewrite(new URL(acceptResult, request.nextUrl));
  }

  return NextResponse.next();
}
