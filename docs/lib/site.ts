export const SITE_NAME = 'BlendGen documentation';
export const SITE_DESCRIPTION =
  'Build synchronized synthetic computer-vision datasets with Blender using BlendGen, including color, depth, normals, optical flow, and material-index passes.';

export const SITE_URL = new URL(
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://blendgen.orfleisher.com',
);

export function absoluteUrl(path = '/') {
  return new URL(path, SITE_URL).toString();
}
