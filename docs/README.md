# BlendGen documentation

The documentation site is a Next.js 16 application built with Fumadocs. Content lives in `content/docs` and navigation is controlled by the colocated `meta.json` files.

## Local development

```bash
cd docs
npm install
npm run dev
```

Open <http://localhost:3000/docs>.

## Validation

```bash
npm run types:check
npm run build
```

The build uses webpack because it is deterministic in constrained and containerized build environments. Fumadocs and Next.js still provide static generation for the content routes.

## Generated Python API reference

```bash
npm run generate:api
```

The generator parses the public modules listed in `scripts/generate_api_docs.py` without importing Blender's `bpy` module. It writes generated MDX to `content/docs/api/generated`. Development, type-check, and build commands run the generator automatically.

## LLM-friendly documentation

- `/llms.txt` is the page-tree index.
- `/llms-full.txt` combines the processed Markdown for every documentation page.
- `/docs/<path>.md` returns the processed Markdown for a single page.
- A request to `/docs/<path>` with a Markdown-preferred `Accept` header receives the same Markdown representation.
