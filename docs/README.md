# BlendGen documentation

The documentation site is a Next.js 16 application built with Fumadocs. Content lives in `content/docs` and navigation is controlled by the colocated `meta.json` files.

## Local development

```bash
cd docs
npm install
npm run dev
```

Open <http://localhost:3000>.

## Validation

```bash
npm run types:check
npm run build
```

Next.js 16 uses Turbopack for both development and production builds. Fumadocs and Next.js statically generate the content routes during production builds.

## Vercel deployment

Configure the Vercel project's **Root Directory** as `docs`. The checked-in `vercel.json` selects the Next.js framework and explicitly sets `.next` as the build output, overriding any stale `public` Output Directory setting in the Vercel dashboard.

The `public` directory is reserved for source assets that should be served unchanged. It is not the output directory for a Next.js application and is not required when there are no such assets.

Vercel Web Analytics is mounted in the root layout. Enable Web Analytics for the project in the Vercel dashboard, deploy, and visit the site to begin collecting page views.

## Generated Python API reference

```bash
npm run generate:api
```

The generator parses the public modules listed in `scripts/generate_api_docs.py` without importing Blender's `bpy` module. It writes generated MDX to `content/docs/api/generated`. Development, type-check, and build commands run the generator automatically.

## LLM-friendly documentation

- `/llms.txt` is the page-tree index.
- `/llms-full.txt` combines the processed Markdown for every documentation page.
- `/<path>.md` returns the processed Markdown for a single page.
- A request to `/<path>` with a Markdown-preferred `Accept` header receives the same Markdown representation.
