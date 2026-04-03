/**
 * Decodes a base64-encoded JPEG string into an object URL
 * that can be set directly on an <img> src.
 *
 * @param {string} b64 - raw base64 string (no data URI prefix)
 * @returns {string} object URL — caller must revoke when done
 */
export function decodeFrame(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: 'image/jpeg' });
  return URL.createObjectURL(blob);
}
