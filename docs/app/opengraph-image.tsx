import { ImageResponse } from 'next/og';

export const alt = 'BlendGen documentation - synthetic computer-vision datasets with Blender';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          alignItems: 'stretch',
          background: '#111111',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          justifyContent: 'space-between',
          padding: '72px 80px',
          width: '100%',
        }}
      >
        <div style={{ color: '#a3a3a3', display: 'flex', fontSize: 26, letterSpacing: '-0.02em' }}>
          BLENDGEN / DOCUMENTATION
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <div style={{ display: 'flex', fontSize: 76, fontWeight: 700, letterSpacing: '-0.06em' }}>
            Synthetic datasets.
            <br />
            Built in Blender.
          </div>
          <div style={{ color: '#b8b8b8', display: 'flex', fontSize: 30 }}>
            Synchronized color, depth, normals, optical flow, and material IDs.
          </div>
        </div>
        <div style={{ alignItems: 'center', display: 'flex', fontSize: 24, justifyContent: 'space-between' }}>
          <span>blendgen.orfleisher.com</span>
          <span style={{ color: '#737373' }}>Python · Blender · Computer vision</span>
        </div>
      </div>
    ),
    size,
  );
}
